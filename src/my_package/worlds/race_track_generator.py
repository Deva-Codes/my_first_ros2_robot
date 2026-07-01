import math

def generate_track_sdf(filename="race_track.sdf", num_segments=150):
    # Track parameters
    lane_width = 3.0
    road_width = 4.0 # Slightly wider than the lanes for a shoulder
    
    # Start building the SDF string
    sdf_content = """<?xml version="1.0" ?>
<sdf version="1.9">
  <world name="curved_race_track">
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>

    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <model name="race_track">
      <static>true</static>
      
      <!-- Grass Background -->
      <link name="grass_plane">
        <pose>0 0 0 0 0 0</pose>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>150 150</size></plane></geometry>
          <material>
            <ambient>0.1 0.4 0.1 1.0</ambient>
            <diffuse>0.1 0.4 0.1 1.0</diffuse>
          </material>
        </visual>
      </link>
"""

    # Generate the curved segments
    for i in range(num_segments):
        t1 = (i / num_segments) * 2 * math.pi
        t2 = ((i + 1) / num_segments) * 2 * math.pi
        
        # Parametric equation for a "Clover/Triangle" shaped sweeping track
        # R(t) = 20 + 5 * cos(3t)
        def get_point(t):
            r = 20.0 + 5.0 * math.cos(3 * t)
            x = r * math.cos(t)
            y = r * math.sin(t)
            
            # Derivatives to find the heading (yaw) of the track at this point
            dr = -15.0 * math.sin(3 * t)
            dx = dr * math.cos(t) - r * math.sin(t)
            dy = dr * math.sin(t) + r * math.cos(t)
            yaw = math.atan2(dy, dx)
            return x, y, yaw

        x1, y1, yaw1 = get_point(t1)
        x2, y2, yaw2 = get_point(t2)
        
        # Distance between points to determine box length (add 10% overlap to prevent gaps)
        ds = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 1.1 
        
        # Calculate positions for the left and right white lines
        # Offset them perpendicularly by exactly half the lane width (1.5m)
        left_x = x1 - (lane_width / 2.0) * math.sin(yaw1)
        left_y = y1 + (lane_width / 2.0) * math.cos(yaw1)
        
        right_x = x1 + (lane_width / 2.0) * math.sin(yaw1)
        right_y = y1 - (lane_width / 2.0) * math.cos(yaw1)

        # Add Asphalt Segment
        sdf_content += f"""
      <link name="asphalt_{i}">
        <pose>{x1} {y1} 0.05 0 0 {yaw1}</pose>
        <visual name="v"><geometry><box><size>{ds} {road_width} 0.1</size></box></geometry>
        <material><ambient>0.15 0.15 0.15 1</ambient><diffuse>0.15 0.15 0.15 1</diffuse></material></visual>
        <collision name="c"><geometry><box><size>{ds} {road_width} 0.1</size></box></geometry></collision>
      </link>"""

        # Add Left Line Segment
        sdf_content += f"""
      <link name="left_line_{i}">
        <pose>{left_x} {left_y} 0.101 0 0 {yaw1}</pose>
        <visual name="v"><geometry><box><size>{ds} 0.15 0.001</size></box></geometry>
        <material><ambient>1 1 1 1</ambient><emissive>0.3 0.3 0.3 1</emissive></material></visual>
      </link>"""

        # Add Right Line Segment
        sdf_content += f"""
      <link name="right_line_{i}">
        <pose>{right_x} {right_y} 0.101 0 0 {yaw1}</pose>
        <visual name="v"><geometry><box><size>{ds} 0.15 0.001</size></box></geometry>
        <material><ambient>1 1 1 1</ambient><emissive>0.3 0.3 0.3 1</emissive></material></visual>
      </link>"""

    # Close the SDF tags
    sdf_content += """
    </model>
  </world>
</sdf>
"""
    
    # Write to file
    with open(filename, "w") as f:
        f.write(sdf_content)
    print(f"Successfully generated {filename}! You can now launch this in Gazebo.")

if __name__ == "__main__":
    generate_track_sdf()