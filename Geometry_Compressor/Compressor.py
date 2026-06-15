# ✅ ===== LOCAL LIBS SETUP (OFFLINE SUPPORT) =====
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

# ✅ ===== ORIGINAL IMPORTS =====
import time
import itertools
import threading
import numpy as np
from pycatia import catia
from tqdm import tqdm

# ✅ ===== STATS =====
stats = {
    "hybrid_bodies_processed": 0, "stable_shapes_joined": 0,
    "unstable_shapes_joined": 0, "shapes_deleted": 0,
    "parameters_deleted": 0, "failed_shapes": [],
    "2d_geometries_deleted": 0, "colors_found": set()
}

# ✅ ===== SPINNER =====
def spinner_animation(msg="Joining..."):
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    stop_event = threading.Event()

    def animate():
        while not stop_event.is_set():
            sys.stdout.write(f"\r{msg} {next(spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)

    threading.Thread(target=animate).start()
    return stop_event


# ✅ ===== COLOR FUNCTIONS =====
def get_surface_color(selection, shapes):
    print("🎯 Attempting to sample color from up to 6 shapes...")
    for shape in shapes[:6]:
        try:
            selection.clear()
            selection.add(shape)
            selection.search("Topology.Face,sel")

            if selection.count >= 1:
                face = selection.item(1)
                if face:
                    selection.clear()
                    selection.add(face)
                    color = selection.vis_properties.get_real_color()

                    if color:
                        rgb = tuple(color)
                        stats["colors_found"].add(rgb)
                        print(f"🎨 Sampled color: RGB = {rgb}")
                        return rgb, 1.0

        except Exception as e:
            print(f"⚠️ Error sampling color from shape {shape.name}: {e}")

    print("⚠️ No color found. Using default (255,255,255)")
    return (255, 255, 255), 0.0


def apply_color(selection, target, color):
    try:
        if color and len(color) >= 3:
            r, g, b = color[:3]
            selection.clear()
            selection.add(target)
            selection.vis_properties.set_real_color(r, g, b, 0)
            print(f"🎨 Applied color: ({r}, {g}, {b})")

    except Exception as e:
        print(f"⚠️ Color apply failed: {e}")


# ✅ ===== GEOMETRY =====
def list_all_shapes(hybrid_body):
    return [
        hybrid_body.hybrid_shapes.item(i)
        for i in range(1, hybrid_body.hybrid_shapes.count + 1)
    ]


def create_join(part, hybrid_body, shapes, selection, join_type="stable"):
    factory = part.hybrid_shape_factory
    valid_refs = []

    for shape in shapes:
        try:
            ref = part.create_reference_from_object(shape)
            valid_refs.append(ref)
        except Exception as e:
            stats["failed_shapes"].append(shape.name)

    if len(valid_refs) < 2:
        print(f"⚠️ Not enough shapes for join ({join_type})")
        return None

    stop_spinner = spinner_animation(f"🔧 Joining {len(valid_refs)} shapes")

    try:
        join = factory.add_new_join(valid_refs[0], valid_refs[1])

        for ref in valid_refs[2:]:
            join.add_element(ref)

        # Join settings
        join.set_connex(0)
        join.set_healing_mode(0)
        join.set_manifold(0)
        join.set_simplify(0)
        join.set_suppress_mode(1)
        join.set_deviation(0.1)
        join.set_angular_tolerance_mode(0)
        join.set_angular_tolerance(0.5)
        join.set_federation_propagation(0)

        hybrid_body.append_hybrid_shape(join)
        part.in_work_object = join
        part.update()

        # Create isolated surface
        ref_join = part.create_reference_from_object(join)
        iso = factory.add_new_surface_datum(ref_join)

        hybrid_body.append_hybrid_shape(iso)
        part.in_work_object = iso
        part.update()

        # Delete originals
        selection.clear()
        for shape in shapes:
            selection.add(shape)
        selection.add(join)
        selection.delete()

        stats["shapes_deleted"] += len(shapes) + 1
        stats["stable_shapes_joined" if "stable" in join_type else "unstable_shapes_joined"] += len(shapes)

        stop_spinner.set()
        print(f"\r✅ Joined {len(valid_refs)} shapes ({join_type})")

        return iso

    except Exception as e:
        stop_spinner.set()
        print(f"\r❌ Join failed: {e}")
        return None


# ✅ ===== PROCESS =====
def process_hybrid_body(part, document, hybrid_body, inherited_color=None):
    stats["hybrid_bodies_processed"] += 1
    selection = document.selection

    print(f"📦 Processing: {hybrid_body.name}")
    shapes = list_all_shapes(hybrid_body)

    color = inherited_color or get_surface_color(selection, shapes)[0]

    if len(shapes) >= 2:
        create_join(part, hybrid_body, shapes, selection, "stable")

    for i in range(1, hybrid_body.hybrid_bodies.count + 1):
        sub = hybrid_body.hybrid_bodies.item(i)

        sub_shapes = list_all_shapes(sub)
        if len(sub_shapes) >= 2:
            create_join(part, sub, sub_shapes, selection, "unstable")

        try:
            selection.clear()
            selection.add(sub)
            selection.vis_properties.set_real_color(*color, 0)
        except:
            pass

        process_hybrid_body(part, document, sub, color)


# ✅ ===== CLEANUP =====
def delete_named_parameters(part, document):
    selection = document.selection
    selection.clear()

    for name in ["BackCircle", "FrontCircle", "RoadLine",
                 "Circle.13", "Circle.14", "Circle.15",
                 "Circle.16", "ACTIVE_AREA"]:
        try:
            param = part.parameters.item(name)
            selection.add(param)
            stats["parameters_deleted"] += 1
        except:
            pass

    if selection.count > 0:
        selection.delete()


def delete_2d_geometries(document):
    selection = document.selection
    selection.clear()

    for pattern in [
        "CATSketchSearch", "CAT2DLSearch", "CATDrwSearch",
        "CATPrtSearch", "CATStFreeStyleSearch"
    ]:
        for geo in ["Line", "Circle", "Curve"]:
            try:
                selection.search(f"({pattern}.{geo}),all")
                count = selection.count
                if count > 0:
                    stats["2d_geometries_deleted"] += count
                    selection.delete()
            except:
                pass
            finally:
                selection.clear()


# ✅ ===== MAIN =====
def process_document(document):
    part = document.part

    delete_2d_geometries(document)

    for i in tqdm(range(1, part.hybrid_bodies.count + 1)):
        process_hybrid_body(part, document, part.hybrid_bodies.item(i))

    delete_named_parameters(part, document)


def main():
    start_time = time.time()

    source = r"C:\Users\50006611\Desktop\recieved data"
    dest = r"C:\Users\50006611\Desktop\optimized data"

    os.makedirs(dest, exist_ok=True)

    files = [f for f in os.listdir(source) if f.lower().endswith(".catpart")]

    print(f"📁 Found {len(files)} files")

    for file in files:
        try:
            caa = catia()
            doc = caa.documents.open(os.path.join(source, file))

            process_document(doc)

            new_name = file.replace(".CATPart", "_Optimized.CATPart")
            doc.save_as(os.path.join(dest, new_name))
            doc.close()

            print(f"✅ Saved: {new_name}")

        except Exception as e:
            print(f"❌ Failed: {file} -> {e}")

    print(f"\n⏱ Completed in {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    main()