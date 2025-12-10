---
title: "Mapping & Understanding Environments"
sidebar_position: 2
description: "SLAM concepts and map types for humanoid robots navigating complex environments"
---

# Mapping & Understanding Environments

## Learning Objectives

By the end of this section, you will:
- Understand Simultaneous Localization and Mapping (SLAM) at a conceptual level
- Learn about different map types used in robotics
- Explore mapping algorithms and their applications
- Apply conceptual understanding to pseudo mapping scenarios

## Introduction

Mapping is the process by which humanoid robots create representations of their environment that enable navigation, planning, and interaction. These maps serve as the robot's memory of spatial relationships, allowing it to return to known locations, plan paths, and avoid obstacles. The challenge lies in creating accurate maps while simultaneously determining the robot's position within those maps—a problem known as Simultaneous Localization and Mapping (SLAM).

For humanoid robots, mapping presents unique challenges compared to wheeled robots. Humanoid robots must consider three-dimensional environments, complex terrain traversability, and the need to maintain balance while navigating. Their maps must account for their specific locomotion capabilities and the dynamic nature of environments where humans operate.

The mapping process involves sensing the environment, extracting features from sensor data, estimating the robot's motion, and updating the map with new information. This process occurs continuously as the robot moves, requiring algorithms that can handle uncertainty, incorporate new observations, and maintain consistent representations over time.

## SLAM: Concept-Level Understanding

Simultaneous Localization and Mapping (SLAM) is one of the most fundamental problems in robotics. At its conceptual level, SLAM addresses how a robot can build a map of an unknown environment while simultaneously using that map to determine its own location. This circular dependency—needing the map to know where you are, but needing to know where you are to build the map—requires sophisticated algorithms that can handle uncertainty and update beliefs incrementally.

The SLAM problem can be understood through a simple analogy: imagine exploring a dark cave with a flashlight and a notepad. As you move through the cave, you use your flashlight to see features in your immediate vicinity. You record these features in your notepad along with your best estimate of where you are relative to them. As you move and see features again from different angles, you can refine both your understanding of where the features are located and where you are in relation to them.

In robotic terms, the SLAM process involves three key components: the motion model, the observation model, and the map representation. The motion model estimates how the robot moves based on control inputs and odometry, though this estimate contains uncertainty. The observation model describes how sensor data relates to the environment, also with uncertainty. The map representation stores the accumulated knowledge about the environment.

SLAM algorithms must handle the fact that both motion and observation estimates are uncertain. They use probabilistic methods to maintain distributions over possible robot poses and map features, updating these distributions as new information becomes available. The goal is to converge on consistent estimates of both robot location and environmental features.

## Map Types and Representations

Robotic maps come in various forms, each suited to different tasks and environments. The choice of map representation affects how efficiently the robot can navigate, plan paths, and understand its environment. Different map types balance accuracy, computational requirements, and suitability for specific applications.

Occupancy grid maps represent space as a collection of cells, each indicating the probability that the space is occupied by an obstacle. These maps are intuitive and support efficient path planning algorithms, making them popular for mobile robots. Each cell contains a value representing the likelihood that the space is free (0.0), occupied (1.0), or unknown (0.5). Grid maps can be updated incrementally as new sensor data arrives.

Topological maps represent the environment as a graph of locations connected by traversable paths. Nodes in the graph represent distinctive places or waypoints, while edges represent navigable connections between them. Topological maps are efficient for path planning over large areas and naturally represent the connectivity of environments. However, they provide limited geometric information for detailed navigation.

Metric maps provide precise geometric information about the environment, often including three-dimensional point clouds or detailed surface models. These maps are essential for tasks requiring precise positioning, such as manipulation or detailed inspection. However, they require significant computational resources to create and maintain, and may be too detailed for high-level navigation tasks.

Hybrid maps combine multiple representation types to leverage the advantages of each. For example, a robot might maintain a coarse topological map for high-level planning while using detailed occupancy grids for local navigation. This approach balances efficiency with accuracy, though it increases system complexity.

Feature-based maps store distinctive environmental landmarks rather than complete geometric information. These maps are efficient and support re-identification of locations, making them useful for long-term navigation and mapping. However, they require robust feature detection and may fail in featureless environments.

## Mapping Algorithms: Pseudo Concepts

Mapping algorithms for humanoid robots must address the unique challenges of legged locomotion and complex three-dimensional environments. These algorithms operate on the principle of incremental map building, where the robot continuously updates its understanding of the environment as it moves and senses.

The basic mapping algorithm follows a cycle of perception, localization, mapping, and planning. In the perception phase, the robot processes sensor data to extract environmental features and identify obstacles. During localization, the robot estimates its position relative to the current map using sensor data and motion estimates. The mapping phase updates the environmental representation with new observations, accounting for uncertainty and sensor noise. Finally, planning determines the robot's next actions based on the updated map and navigation goals.

Extended Kalman Filter (EKF) SLAM represents both the robot's pose and landmark positions as a joint probability distribution, updating this distribution as new observations are made. While conceptually elegant, EKF SLAM scales quadratically with the number of landmarks, limiting its use to environments with relatively few distinctive features.

Graph-based SLAM formulates the mapping problem as an optimization task, where the goal is to find the most likely robot trajectory and landmark positions given all observations. This approach can handle large numbers of constraints and observations, making it suitable for complex mapping tasks. The solution involves minimizing an error function that represents the discrepancy between predicted and observed measurements.

Particle filter SLAM maintains multiple hypotheses about robot pose and map, with each particle representing a possible state. As observations are made, particles that are inconsistent with the data are discarded while those that match well are preserved and replicated. This approach naturally handles multimodal uncertainty but requires significant computational resources.

Visual SLAM uses camera imagery to create maps, extracting and tracking visual features across multiple frames. This approach can create rich environmental representations using relatively lightweight sensors. However, visual SLAM can fail in textureless environments or under changing lighting conditions.

## Practical Application: Pseudo Mapping

Consider a humanoid robot entering an unknown building to perform a search and rescue operation. The robot begins with no knowledge of the building layout and must simultaneously create a map while navigating to find potential victims.

Initially, the robot's map is empty, and its position is unknown. As the robot moves forward, its sensors detect walls, doorways, and furniture. The mapping algorithm processes these observations, creating the first features in the map and estimating the robot's initial position relative to them.

As the robot continues exploring, it detects a distinctive feature—a red fire extinguisher—that it has seen before from a different location. This loop closure allows the algorithm to correct accumulated positioning errors and create a more consistent map. The robot now knows that the path it followed to reach the fire extinguisher connects back to the path where it first saw the extinguisher.

The robot builds increasingly detailed representations of corridors, rooms, and obstacles. It identifies areas that have been thoroughly explored and areas that remain unknown. The map guides the robot's exploration strategy, directing it toward unexplored regions while avoiding already-mapped obstacles.

Throughout this process, the robot maintains uncertainty estimates for both its position and the map features. When sensor data is ambiguous or motion estimates are uncertain, the algorithm increases uncertainty appropriately. When new observations provide clear information, the algorithm reduces uncertainty and refines estimates.

The resulting map serves multiple purposes: it enables the robot to navigate back to the entrance, provides information about the building layout for human operators, and supports path planning for continued exploration. The map also serves as a foundation for future visits to the same environment.

:::tip Practical Application
See [Example 9: Mapping Concepts](../../code/module-3/example-09) for hands-on implementation of basic mapping concepts.
:::

## Challenges and Considerations

Mapping for humanoid robots faces several unique challenges that don't affect wheeled robots to the same degree. These challenges include the need to map in three dimensions, the complexity of legged locomotion, and the dynamic nature of human environments.

Three-dimensional mapping is essential for humanoid robots, which must consider not just floor plans but also obstacles at different heights, traversable surfaces, and areas that may be safe for walking but not for other activities. This requires more complex sensor systems and computational approaches compared to two-dimensional mapping.

Dynamic environments pose particular challenges for mapping. Unlike static maps of fixed structures, humanoid robots must operate in environments where furniture moves, doors open and close, and people create temporary obstacles. Mapping systems must distinguish between permanent and temporary features while remaining responsive to environmental changes.

Sensor limitations affect mapping quality and reliability. Different sensors have different strengths and weaknesses: cameras provide rich information but may fail in poor lighting, LIDAR provides accurate distance measurements but may miss transparent obstacles, and sonar can detect soft obstacles but has limited resolution. Effective mapping systems must integrate information from multiple sensors.

Computational constraints limit the complexity of mapping algorithms that can run in real-time on humanoid robot platforms. While sophisticated mapping approaches may provide better results, they may exceed the computational capabilities of robot hardware. The challenge is to find approaches that provide adequate mapping performance within computational constraints.

## Summary

Mapping and environment understanding form the foundation of autonomous navigation for humanoid robots. The SLAM problem, while conceptually complex, enables robots to operate in unknown environments by simultaneously building maps and determining their location within those maps. Different map types—occupancy grids, topological maps, metric maps, and hybrid approaches—offer different trade-offs between accuracy, efficiency, and applicability.

The challenges of three-dimensional mapping, dynamic environments, sensor limitations, and computational constraints require careful consideration in mapping system design. Successful humanoid robot mapping systems must balance these competing requirements while providing the spatial awareness necessary for safe and effective navigation.

Understanding mapping concepts provides the foundation for implementing more sophisticated navigation and planning capabilities in humanoid robots. The ability to create and maintain environmental representations enables robots to operate in the complex, three-dimensional world designed for human activity.

## Further Reading

- Probabilistic Robotics by Thrun, Burgard, and Fox
- Simultaneous Localization and Mapping: A Survey of Current Methods by Rekhi et al.
- Visual SLAM: Why Bundle Adjust? by Strasdat et al.