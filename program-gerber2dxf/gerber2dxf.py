#!/usr/bin/env python3
"""
Gerber to DXF Converter
Converts PCB Gerber files to DXF format using gerbonara library
"""

import os
import sys
import math
from pathlib import Path
import ezdxf
from gerbonara import GerberFile
from gerbonara.graphic_objects import Line, Arc, Region, Flash


def convert_gerber_to_dxf(gerber_path, dxf_path, layer_name=None):
    """
    Convert a single Gerber file to DXF format

    Args:
        gerber_path: Path to input Gerber file
        dxf_path: Path to output DXF file
        layer_name: Optional layer name in DXF
    """
    print(f"Converting {gerber_path} to {dxf_path}...")

    try:
        # Load Gerber file
        gerber = GerberFile.open(gerber_path)

        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        # Set layer name
        if layer_name is None:
            layer_name = Path(gerber_path).name

        # Create layer
        doc.layers.add(layer_name)

        # Convert each graphic object
        converted_count = 0
        for obj in gerber.objects:
            try:
                if isinstance(obj, Line):
                    # Convert line
                    msp.add_line(
                        (obj.x1, obj.y1),
                        (obj.x2, obj.y2),
                        dxfattribs={'layer': layer_name}
                    )
                    converted_count += 1

                elif isinstance(obj, Arc):
                    # Convert arc
                    # NOTE: gerbonara Arc.cx, Arc.cy are RELATIVE to start point
                    # Use Arc.center property for absolute coordinates
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
                    # Convert region (polygon)
                    vertices = []

                    # Region outline can be tuples or Line/Arc objects
                    for segment in obj.outline:
                        if isinstance(segment, tuple) and len(segment) >= 2:
                            # Direct coordinate tuple
                            vertices.append((segment[0], segment[1]))
                        elif hasattr(segment, 'x1') and hasattr(segment, 'y1'):
                            # Line/Arc object
                            vertices.append((segment.x1, segment.y1))
                            if hasattr(segment, 'x2') and hasattr(segment, 'y2'):
                                vertices.append((segment.x2, segment.y2))

                    # Remove duplicate consecutive points
                    unique_vertices = []
                    for v in vertices:
                        if not unique_vertices or abs(v[0] - unique_vertices[-1][0]) > 0.001 or abs(v[1] - unique_vertices[-1][1]) > 0.001:
                            unique_vertices.append(v)

                    if len(unique_vertices) >= 3:
                        # Close polygon if not already closed
                        if abs(unique_vertices[0][0] - unique_vertices[-1][0]) > 0.001 or abs(unique_vertices[0][1] - unique_vertices[-1][1]) > 0.001:
                            unique_vertices.append(unique_vertices[0])

                        msp.add_lwpolyline(
                            unique_vertices,
                            dxfattribs={'layer': layer_name}
                        )
                        converted_count += 1

                elif isinstance(obj, Flash):
                    # Convert flash (pad/via)
                    aperture = obj.aperture
                    aperture_type = type(aperture).__name__

                    if aperture_type == 'CircleAperture':
                        # Circle aperture
                        if hasattr(aperture, 'diameter'):
                            radius = aperture.diameter / 2
                            msp.add_circle(
                                center=(obj.x, obj.y),
                                radius=radius,
                                dxfattribs={'layer': layer_name}
                            )
                            converted_count += 1

                    elif aperture_type == 'RectangleAperture':
                        # Rectangle aperture
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
                        # Obround - approximate as rectangle
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
                        # Complex aperture macro - decompose to primitives
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
                                # Rectangle with rotation
                                w = prim.w / 2
                                h = prim.h / 2
                                cx, cy = prim.x, prim.y

                                cos_r = math.cos(math.radians(prim.rotation))
                                sin_r = math.sin(math.radians(prim.rotation))

                                # Four corners
                                corners = [
                                    (-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)
                                ]

                                # Rotate and translate
                                points = []
                                for x, y in corners:
                                    rx = cx + x * cos_r - y * sin_r
                                    ry = cx + x * sin_r + y * cos_r
                                    points.append((rx, ry))

                                msp.add_lwpolyline(
                                    points,
                                    dxfattribs={'layer': layer_name}
                                )

                        converted_count += 1

                    else:
                        # Unknown aperture - try equivalent_width
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
                # Skip problematic objects
                pass

        # Save DXF
        doc.saveas(dxf_path)
        print(f"✓ Saved: {dxf_path} ({converted_count}/{len(gerber.objects)} objects)")

    except Exception as e:
        print(f"✗ Error converting {gerber_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def convert_all_gerber_files(input_dir, output_dir):
    """
    Convert all Gerber files in a directory to DXF

    Args:
        input_dir: Directory containing Gerber files
        output_dir: Directory for output DXF files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

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
    print("-" * 60)

    # Convert each file
    success_count = 0
    for gerber_file in gerber_files:
        # Use full filename + original extension in the name
        # to avoid overwriting files with same base name
        dxf_file = output_path / f"{gerber_file.name}.dxf"
        if convert_gerber_to_dxf(str(gerber_file), str(dxf_file)):
            success_count += 1

    print("-" * 60)
    print(f"Conversion complete: {success_count}/{len(gerber_files)} files successful")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python gerber2dxf.py <gerber_directory> [output_directory]")
        print("\nExample:")
        print("  python gerber2dxf.py ./Gerber ./output")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)

    convert_all_gerber_files(input_dir, output_dir)


if __name__ == "__main__":
    main()
