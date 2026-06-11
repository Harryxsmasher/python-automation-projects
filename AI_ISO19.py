import os
import time
import itertools
import sys
import threading
import numpy as np
from pycatia import catia
from tqdm import tqdm

stats = {
    "hybrid_bodies_processed": 0, "stable_shapes_joined": 0,
    "unstable_shapes_joined": 0, "shapes_deleted": 0,
    "parameters_deleted": 0, "failed_shapes": [],
    "2d_geometries_deleted": 0, "colors_found": set()
}

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

def get_surface_color(selection, shapes):
    print("🎯 Attempting to sample color from up to 6 shapes...")
    for shape in shapes[:6]:  # Limit to first six shapes
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
    print("⚠️ No color found in first six shapes. Using default color (255, 255, 255).")
    return (255, 255, 255), 0.0

def apply_color(selection, target, color):
    try:
        if color and len(color) >= 3:
            r, g, b = color[:3]
            selection.clear()
            selection.add(target)
            selection.vis_properties.set_real_color(r, g, b, 0)
            print(f"🎨 Applied color: RGB = ({r}, {g}, {b})")
    except Exception as e:
        print(f"⚠️ Failed to apply color: {e}")

def list_all_shapes(hybrid_body):
    return [hybrid_body.hybrid_shapes.item(i) for i in range(1, hybrid_body.hybrid_shapes.count + 1)]
def create_join(part, hybrid_body, shapes, selection, join_type="stable"):
    hybrid_shape_factory = part.hybrid_shape_factory
    valid_refs = []
    for shape in shapes:
        try:
            ref = part.create_reference_from_object(shape)
            valid_refs.append(ref)
        except Exception as e:
            stats["failed_shapes"].append(shape.name)
            print(f"⚠️ Failed to create reference for shape {shape.name}: {e}")

    if len(valid_refs) < 2:
        print(f"⚠️ Not enough valid shapes to join ({join_type}).")
        return None

    stop_spinner = spinner_animation(f"🔧 Joining {len(valid_refs)} shapes ({join_type})")
    try:
        join = hybrid_shape_factory.add_new_join(valid_refs[0], valid_refs[1])
        for ref in valid_refs[2:]:
            join.add_element(ref)
        join.set_connex(0); join.set_healing_mode(0); join.set_manifold(0)
        join.set_simplify(0); join.set_suppress_mode(1); join.set_deviation(0.1)
        join.set_angular_tolerance_mode(0); join.set_angular_tolerance(0.5)
        join.set_federation_propagation(0)

        hybrid_body.append_hybrid_shape(join)
        part.in_work_object = join
        part.update()

        ref_join = part.create_reference_from_object(join)
        isolated = hybrid_shape_factory.add_new_surface_datum(ref_join)
        hybrid_body.append_hybrid_shape(isolated)
        part.in_work_object = isolated
        part.update()

        selection.clear()
        for shape in shapes:
            selection.add(shape)
        selection.add(join)
        selection.delete()

        stats["shapes_deleted"] += len(shapes) + 1
        stats["stable_shapes_joined" if "stable" in join_type else "unstable_shapes_joined"] += len(shapes)
        stop_spinner.set()
        print(f"\r✅ Joined {len(valid_refs)} shapes ({join_type})")
        return isolated
    except Exception as e:
        stop_spinner.set()
        print(f"\r❌ Failed to join shapes ({join_type}): {e}")
        return None

def process_hybrid_body(part, document, hybrid_body, inherited_color=None):
    stats["hybrid_bodies_processed"] += 1
    selection = document.selection

    print(f"📦 Processing hybrid body: {hybrid_body.name}")
    shapes = list_all_shapes(hybrid_body)

    color = inherited_color
    if color is None:
        color, _ = get_surface_color(selection, shapes)

    if len(shapes) >= 2:
        create_join(part, hybrid_body, shapes, selection, "stable")

    sub_body_count = hybrid_body.hybrid_bodies.count
    if sub_body_count > 0:
        print(f"📂 Found {sub_body_count} sub-hybrid bodies in {hybrid_body.name}")
        for i in range(1, sub_body_count + 1):
            sub_body = hybrid_body.hybrid_bodies.item(i)

            sub_shapes = list_all_shapes(sub_body)
            if len(sub_shapes) >= 2:
                create_join(part, sub_body, sub_shapes, selection, "unstable")

            try:
                selection.clear()
                selection.add(sub_body)
                selection.vis_properties.set_real_color(*color, 0)
                print(f"🎨 Applied color to sub-body: {sub_body.name}")
            except Exception as e:
                print(f"⚠️ Failed to apply color to sub-body {sub_body.name}: {e}")

            process_hybrid_body(part, document, sub_body, inherited_color=color)

def delete_named_parameters(part, document):
    print("🧹 Deleting named parameters...")
    selection = document.selection
    selection.clear()
    for name in ["BackCircle", "FrontCircle", "RoadLine", "Circle.13", "Circle.14", "Circle.15", "Circle.16", "ACTIVE_AREA"]:
        try:
            param = part.parameters.item(name)
            selection.add(param)
            stats["parameters_deleted"] += 1
        except Exception as e:
            print(f"⚠️ Could not find parameter {name}: {e}")
    if selection.count > 0:
        selection.delete()
        print(f"✅ Deleted {selection.count} named parameters.")
    else:
        print("ℹ️ No named parameters found.")

def delete_2d_geometries(document):
    print("🧹 Searching and deleting 2D geometries...")
    selection = document.selection
    selection.clear()

    geo_types = ["Line", "Circle", "Curve"]
    search_patterns = [
        "CATSketchSearch", "CAT2DLSearch", "CATDrwSearch",
        "CATPrtSearch", "CATStFreeStyleSearch", "CATGmoSearch", "CATSpdSearch"
    ]

    for pattern in search_patterns:
        for geo_type in geo_types:
            query = f"({pattern}.{geo_type}),all"
            try:
                selection.search(query)
                count = selection.count
                if count > 0:
                    print(f"🧹 Deleting {count} items: {query}")
                    stats["2d_geometries_deleted"] += count
                    selection.delete()
            except Exception as e:
                print(f"⚠️ Search failed for {query}: {e}")
            finally:
                selection.clear()

def print_summary(start_time):
    elapsed = time.time() - start_time
    print("\n📊 Summary Report")
    for key, label in [
        ("hybrid_bodies_processed", "Hybrid Bodies Processed"),
        ("stable_shapes_joined", "Stable Shapes Joined"),
        ("unstable_shapes_joined", "Unstable Shapes Joined"),
        ("shapes_deleted", "Shapes Deleted"),
        ("parameters_deleted", "Parameters Deleted"),
        ("2d_geometries_deleted", "2D Geometries Deleted")
    ]:
        print(f"{label}: {stats[key]}")
    print(f"Failed Shapes: {stats['failed_shapes']}")
    print(f"Unique Colors Found: {len(stats['colors_found'])}")
    for color in stats["colors_found"]:
        print(f" - RGB: {color}")
    print(f"⏱️ Time Taken: {elapsed:.2f} seconds\n✅ Processing complete.")

def process_document(document):
    part = document.part
    print(f"📄 Starting document: {document.name}")
    delete_2d_geometries(document)
    for i in tqdm(range(1, part.hybrid_bodies.count + 1), desc=f"Top-level bodies in {document.name}", unit="body", leave=True):
        hybrid_body = part.hybrid_bodies.item(i)
        process_hybrid_body(part, document, hybrid_body)
    delete_named_parameters(part, document)

def main():
    start_time = time.time()
    source_folder = r"C:\Users\50006611\Desktop\recieved data"
    destination_folder = r"C:\Users\50006611\Desktop\optimized data"
    os.makedirs(destination_folder, exist_ok=True)

    catpart_files = [f for f in os.listdir(source_folder) if f.lower().endswith(".catpart")]
    print(f"📁 Found {len(catpart_files)} CATPart files to process.")

    for file_name in catpart_files:
        print(f"\n📂 Opening: {file_name}")
        try:
            caa = catia()
            document = caa.documents.open(os.path.join(source_folder, file_name))
            process_document(document)

            new_name = f"{os.path.splitext(file_name)[0]}_Optimized.CATPart"
            destination_path = os.path.join(destination_folder, new_name)

            document.save_as(destination_path)
            document.close()
            print(f"✅ Saved optimized file: {new_name}")
        except Exception as e:
            print(f"❌ Failed to process {file_name}: {e}")
            try: document.close()
            except: pass

    print_summary(start_time)

if __name__ == "__main__":
    main()
