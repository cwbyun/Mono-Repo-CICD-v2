#!/usr/bin/env python3
"""
Gerber to DXF Converter - Merged Version
Converts multiple PCB Gerber files into ONE DXF file with multiple layers
"""

import os
import sys
import math
from pathlib import Path
import ezdxf
from gerbonara import GerberFile
from gerbonara.graphic_objects import Line, Arc, Region, Flash


# 레이어별 색상 정의
LAYER_COLORS = {
    'GTL': 1,    # Red - Top Copper
    'GBL': 5,    # Blue - Bottom Copper
    'GTO': 2,    # Yellow - Top Overlay/Silkscreen
    'GBO': 2,    # Yellow - Bottom Overlay
    'GTS': 3,    # Green - Top Solder Mask
    'GBS': 3,    # Green - Bottom Solder Mask
    'GKO': 7,    # White - Keepout/Outline
    'G1': 6,     # Magenta - Inner Layer 1
    'G2': 6,     # Magenta - Inner Layer 2
    'G3': 6,     # Magenta - Inner Layer 3
    'G4': 6,     # Magenta - Inner Layer 4
    'GD1': 8,    # Dark Gray - Drill
    'GG1': 4,    # Cyan - Ground
}


def add_gerber_to_dxf(doc, msp, gerber_path, layer_name):
    """
    Add Gerber file content to existing DXF document

    Args:
        doc: ezdxf document
        msp: modelspace
        gerber_path: Path to input Gerber file
        layer_name: Layer name in DXF

    Returns:
        tuple: (converted_count, total_count)
    """
    try:
        # Load Gerber file
        gerber = GerberFile.open(gerber_path)

        # Create layer with color
        layer_color = LAYER_COLORS.get(layer_name.upper(), 7)  # Default white
        doc.layers.add(layer_name, color=layer_color)

        # Convert each graphic object
        converted_count = 0
        for obj in gerber.objects:
            try:
                if isinstance(obj, Line):
                    msp.add_line(
                        (obj.x1, obj.y1),
                        (obj.x2, obj.y2),
                        dxfattribs={'layer': layer_name}
                    )
                    converted_count += 1

                elif isinstance(obj, Arc):
                    # NOTE: gerbonara Arc.cx, Arc.cy are RELATIVE to start point
                    center = obj.center
                    center_x = center.x if hasattr(center, 'x') else (obj.x1 + obj.cx)
                    center_y = center.y if hasattr(center, 'y') else (obj.y1 + obj.cy)

                    # Radius is the distance from center to start point
                    radius = math.sqrt(obj.cx**2 + obj.cy**2)

                    # Calculate angles
                    start_angle = math.degrees(math.atan2(obj.y1 - center_y, obj.x1 - center_x))
                    end_angle = math.degrees(math.atan2(obj.y2 - center_y, obj.x2 - center_x))

                    if obj.clockwise:
                        start_angle, end_angle = end_angle, start_angle

                    msp.add_arc(
                        center=(center_x, center_y),
                        radius=radius,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        dxfattribs={'layer': layer_name}
                    )
                    converted_count += 1

                elif isinstance(obj, Region):
                    vertices = []

                    for segment in obj.outline:
                        if isinstance(segment, tuple) and len(segment) >= 2:
                            vertices.append((segment[0], segment[1]))
                        elif hasattr(segment, 'x1') and hasattr(segment, 'y1'):
                            vertices.append((segment.x1, segment.y1))
                            if hasattr(segment, 'x2') and hasattr(segment, 'y2'):
                                vertices.append((segment.x2, segment.y2))

                    unique_vertices = []
                    for v in vertices:
                        if not unique_vertices or abs(v[0] - unique_vertices[-1][0]) > 0.001 or abs(v[1] - unique_vertices[-1][1]) > 0.001:
                            unique_vertices.append(v)

                    if len(unique_vertices) >= 3:
                        if abs(unique_vertices[0][0] - unique_vertices[-1][0]) > 0.001 or abs(unique_vertices[0][1] - unique_vertices[-1][1]) > 0.001:
                            unique_vertices.append(unique_vertices[0])

                        msp.add_lwpolyline(
                            unique_vertices,
                            dxfattribs={'layer': layer_name}
                        )
                        converted_count += 1

                elif isinstance(obj, Flash):
                    aperture = obj.aperture
                    aperture_type = type(aperture).__name__

                    if aperture_type == 'CircleAperture':
                        if hasattr(aperture, 'diameter'):
                            radius = aperture.diameter / 2
                            msp.add_circle(
                                center=(obj.x, obj.y),
                                radius=radius,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'RectangleAperture':
                        if hasattr(aperture, 'w'):
                            w = aperture.w / 2
                            h = getattr(aperture, 'h', aperture.w) / 2
                            points = [
                                (obj.x - w, obj.y - h),
                                (obj.x + w, obj.y - h),
                                (obj.x + w, obj.y + h),
                                (obj.x - w, obj.y + h),
                                (obj.x - w, obj.y - h)
                            ]
                            msp.add_lwpolyline(
                                points,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'ObroundAperture':
                        if hasattr(aperture, 'w'):
                            w = aperture.w / 2
                            h = getattr(aperture, 'h', aperture.w) / 2
                            points = [
                                (obj.x - w, obj.y - h),
                                (obj.x + w, obj.y - h),
                                (obj.x + w, obj.y + h),
                                (obj.x - w, obj.y + h),
                                (obj.x - w, obj.y - h)
                            ]
                            msp.add_lwpolyline(
                                points,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'ApertureMacroInstance':
                        primitives = aperture.flash(obj.x, obj.y, obj.unit, obj.polarity_dark)
                        for prim in primitives:
                            prim_type = type(prim).__name__

                            if prim_type == 'Circle':
                                msp.add_circle(
                                    center=(prim.x, prim.y),
                                    radius=prim.r,
                                    dxfattribs={'layer': layer_name}
                                )
                            elif prim_type == 'Rectangle':
                                w = prim.w / 2
                                h = prim.h / 2
                                cx, cy = prim.x, prim.y

                                cos_r = math.cos(math.radians(prim.rotation))
                                sin_r = math.sin(math.radians(prim.rotation))

                                corners = [
                                    (-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)
                                ]

                                points = []
                                for x, y in corners:
                                    rx = cx + x * cos_r - y * sin_r
                                    ry = cy + x * sin_r + y * cos_r
                                    points.append((rx, ry))

                                msp.add_lwpolyline(
                                    points,
                                    dxfattribs={'layer': layer_name}
                                )

                        converted_count += 1

                    else:
                        if hasattr(aperture, 'equivalent_width'):
                            try:
                                width = aperture.equivalent_width()
                                if callable(width):
                                    width = width()
                                radius = width / 2
                                msp.add_circle(
                                    center=(obj.x, obj.y),
                                    radius=radius,
                                    dxfattribs={'layer': layer_name}
                                )
                                converted_count += 1
                            except:
                                pass

            except Exception:
                pass

        return converted_count, len(gerber.objects)

    except Exception as e:
        print(f"✗ Error processing {gerber_path}: {e}")
        return 0, 0


def merge_gerber_files(input_dir, output_file):
    """
    Merge all Gerber files into one DXF file with multiple layers

    Args:
        input_dir: Directory containing Gerber files
        output_file: Output DXF file path
    """
    input_path = Path(input_dir)

    # Common Gerber file extensions
    gerber_extensions = [
        '.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs',
        '.gko', '.g1', '.g2', '.g3', '.g4', '.gd1', '.gg1'
    ]

    # Find all Gerber files
    gerber_files = []
    for ext in gerber_extensions:
        gerber_files.extend(input_path.glob(f'*{ext}'))
        gerber_files.extend(input_path.glob(f'*{ext.upper()}'))

    if not gerber_files:
        print(f"No Gerber files found in {input_dir}")
        return

    print(f"Found {len(gerber_files)} Gerber files")
    print(f"Merging into: {output_file}")
    print("-" * 60)

    # Create DXF document
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Add each Gerber file as a layer
    total_converted = 0
    total_objects = 0

    for gerber_file in gerber_files:
        # Extract layer name from filename (e.g., GTL, GBL)
        layer_name = gerber_file.suffix[1:].upper()  # Remove dot, uppercase

        print(f"Processing {gerber_file.name} -> Layer: {layer_name}")

        converted, total = add_gerber_to_dxf(doc, msp, str(gerber_file), layer_name)
        total_converted += converted
        total_objects += total

        print(f"  ✓ {converted}/{total} objects")

    # Save merged DXF
    doc.saveas(output_file)

    print("-" * 60)
    print(f"✓ Merged DXF saved: {output_file}")
    print(f"  Total layers: {len(gerber_files)}")
    print(f"  Total objects: {total_converted}/{total_objects}")
    print(f"\n레이어 색상:")
    for layer, color_code in LAYER_COLORS.items():
        color_names = {1: 'Red', 2: 'Yellow', 3: 'Green', 4: 'Cyan', 5: 'Blue', 6: 'Magenta', 7: 'White', 8: 'Gray'}
        print(f"  {layer}: {color_names.get(color_code, 'Unknown')}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python gerber2dxf_merged.py <gerber_directory> [output_file.dxf]")
        print("\nExample:")
        print("  python gerber2dxf_merged.py ./Gerber merged.dxf")
        print("\nThis will create ONE DXF file with all Gerber files as separate layers")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "merged.dxf"

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)

    merge_gerber_files(input_dir, output_file)


if __name__ == "__main__":
    main()
