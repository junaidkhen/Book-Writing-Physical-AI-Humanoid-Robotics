---
title: "Week 3: Motor Control & Action"
sidebar_position: 3
description: "Learn how robots translate digital commands into physical movement through motors, actuators, and control systems"
keywords: [motor-control, actuators, locomotion, balance, stability, robot-movement]
---

# Week 3: Motor Control & Action

## Learning Objectives

By the end of this week, you will:
- Understand how robots translate digital commands into physical movements
- Learn the basics of locomotion and balance in humanoid robots
- Recognize the challenges of controlling complex mechanical systems
- Appreciate the difference between simple position control and dynamic movement

## Introduction: From Bits to Motion

In Week 2, we explored how robots sense the world—translating physical phenomena into digital signals. This week, we tackle the opposite challenge: **how do robots translate digital commands into physical actions?**

When you decide to pick up a coffee cup, your brain sends signals to hundreds of muscles, coordinating their contractions in precise timing and force to execute smooth, controlled movement. You don't consciously think about individual muscle activations—you just "will" your hand to move, and it happens.

Robots face the same challenge, but without the benefit of millions of years of evolutionary optimization. Every movement must be explicitly programmed or learned, requiring coordination of motors, management of forces, maintenance of balance, and continuous adaptation to unexpected disturbances.

This week, we explore the fascinating world of robot motion: how actuators work, how robots maintain stability, and why making a robot walk is one of the hardest problems in robotics.

## Actuators: The Robot's Muscles

Just as muscles contract to move your bones, **actuators** generate forces to move robot joints and limbs.

### Types of Actuators

**1. Electric Motors**

The most common actuators in robotics:

**How They Work** (Conceptual):
- Electrical current flows through coils creating magnetic fields
- Magnetic fields interact with permanent magnets to create rotational force (torque)
- Rotation is transmitted to joints through gears and linkages

**Advantages**:
- Precise control
- Quiet operation
- Wide range of sizes and power levels
- Well-understood technology

**Disadvantages**:
- Lower power-to-weight ratio than hydraulics
- Can overheat under sustained high loads
- Require gearing for high torque (adding weight and complexity)

**Example**: Small servo motors in robot fingers, large motors in hip and knee joints

**2. Hydraulic Actuators**

Used in large, powerful robots:

**How They Work** (Conceptual):
- Pressurized fluid (oil) is pumped through cylinders
- Fluid pressure pushes pistons, creating linear force
- Very high forces can be generated

**Advantages**:
- Extremely high power-to-weight ratio
- Can generate massive forces
- Self-cooling (fluid carries away heat)

**Disadvantages**:
- Requires heavy pumps and fluid reservoirs
- Can leak
- Noisy
- More complex control

**Example**: Boston Dynamics' Atlas robot uses hydraulics for dynamic movements like jumping and backflips

**3. Pneumatic Actuators**

Use compressed air instead of hydraulic fluid:

**Advantages**:
- Clean (air leaks harmless)
- Simple and inexpensive
- Inherently compliant (soft, safe)

**Disadvantages**:
- Less precise control
- Lower forces than hydraulics
- Requires air compressor

**Example**: Soft robotic grippers, some industrial automation

### From Actuator to Movement

The basic control loop for an actuator looks like this:

1. **Command**: "Move joint to 45 degrees"
2. **Sensor Reading**: "Joint is currently at 30 degrees"
3. **Error Calculation**: "Need to move 15 degrees more"
4. **Control Signal**: "Apply torque to motor"
5. **Motion**: Motor turns, joint angle changes
6. **Feedback**: Read new sensor value
7. **Repeat**: Until joint reaches target (or close enough)

This happens continuously, typically hundreds of times per second.

## Locomotion: The Challenge of Walking

For wheeled robots, motion is straightforward: turn the wheels, and the robot moves. But humanoid robots walk on two legs—a feat that requires constant dynamic balance.

### Why Walking is Hard

Consider what happens when you take a step:

1. **Shift Weight**: Transfer weight to one leg
2. **Lift Foot**: Raise the other foot off the ground
3. **Swing Leg**: Move the leg forward
4. **Plant Foot**: Place foot on ground
5. **Transfer Weight**: Shift weight to forward leg
6. **Repeat**: With the other leg

Seems simple? Consider the hidden complexities:

- While one foot is in the air, you're balancing on a single point of contact
- Your center of mass must stay over your support foot, or you'll fall
- Each step involves controlled falling forward and catching yourself
- Unexpected disturbances (bumps, slips) require instant corrections
- Different speeds require different gaits

### The Center of Mass Challenge

A fundamental concept in robot balance:

**Center of Mass (CoM)**: The point where all of the robot's mass can be considered concentrated

**For stability**, the CoM projection (straight down to the ground) must remain within the **support polygon**—the area on the ground where the robot has contact.

**Standing on Two Feet**:
- Support polygon = area between and around both feet
- Relatively large, stable
- Robot can lean slightly without falling

**Standing on One Foot** (during step):
- Support polygon = just the contact area of one foot
- Very small, unstable
- Robot must keep CoM precisely over that foot

**In Motion**:
- CoM is constantly shifting
- Must be dynamically balanced (like riding a bicycle)
- Requires continuous adjustments

**Conceptual Example**: Try standing on one foot with your eyes closed. Notice how your ankle constantly makes tiny adjustments to keep you balanced? A humanoid robot must do this continuously, using sensors and motors instead of muscles and nerves.

### Gait Patterns

Different walking speeds and terrains require different **gaits**:

**1. Static Walking**
- Always keep CoM within support polygon
- Very stable but slow
- At least one foot always on ground
- Like a careful tiptoe walk

**2. Dynamic Walking**
- CoM can move outside support polygon momentarily
- Faster, more natural
- Periods where both feet off ground
- Like normal human walking or running

**3. Running**
- Extended flight phase (both feet off ground)
- High-speed, high-impact
- Requires sophisticated control
- Very challenging for robots

Most current humanoid robots use dynamic walking but struggle with running. Some advanced robots (like Boston Dynamics' Atlas) can run and jump, but this requires cutting-edge control algorithms and powerful actuators.

## Balance and Stability

Maintaining balance is one of the most critical challenges in humanoid robotics.

### Static Stability

**Definition**: The robot will remain upright even if all motors stop

**Requirement**: CoM must be within support polygon

**Advantage**: Very safe—robot won't fall if power is lost

**Disadvantage**: Slow, limited to simple movements

###  Dynamic Stability

**Definition**: The robot maintains balance through active control, even if momentarily unstable

**Requirement**: Robot can recover balance through corrective actions

**Advantage**: Faster, more versatile, more human-like movement

**Disadvantage**: Requires constant power and active control; risk of falling if control fails

### Balance Control Strategies

Robots use several strategies to maintain balance:

**1. Ankle Strategy**
- Make small adjustments by rotating ankles
- Good for small disturbances while standing
- Limited range of correction

**2. Hip Strategy**
- Move hips to shift CoM
- Larger corrections than ankle strategy
- Used for moderate disturbances

**3. Stepping Strategy**
- Take a step to create new support polygon under shifted CoM
- Most powerful correction
- Used when ankle and hip strategies insufficient

**Conceptual Example**: Imagine standing on a bus that suddenly brakes:
- **Ankle Strategy**: You tense your ankles to stay upright (small disturbance)
- **Hip Strategy**: You lean back at the hips to counteract forward momentum (medium disturbance)
- **Stepping Strategy**: You take a step forward to catch yourself (large disturbance)

### Disturbance Handling

The real world is full of unexpected disturbances:
- Uneven floors
- Bumps and obstacles
- Slippery surfaces
- Being pushed or jostled
- Carrying varying loads

A robust humanoid robot must:
1. **Detect** disturbances quickly (through IMU, force sensors)
2. **Assess** severity (ankle/hip/stepping strategy needed?)
3. **React** fast enough to prevent falling (milliseconds count)
4. **Recover** gracefully and continue the task

Advanced robots can handle significant disturbances—being pushed, walking on ice, stepping on unstable surfaces—but this requires sophisticated sensing and control.

## Control Systems: From Simple to Sophisticated

Robot control ranges from simple to highly complex:

### Basic Position Control

**Goal**: Move joint to desired angle

**Method**:
- Measure current angle
- Calculate error (desired - current)
- Apply torque proportional to error (PID control)
- Repeat until error is small

**Good For**: Simple, slow movements

**Limitations**: Doesn't account for dynamics, forces, or interactions

### Trajectory Control

**Goal**: Follow a planned path over time

**Method**:
- Plan sequence of positions over time
- Track planned trajectory, correcting errors
- Smoother, more coordinated movements

**Good For**: Reaching, manipulation, walking on flat ground

**Limitations**: Struggles with unexpected disturbances or contact forces

### Force Control

**Goal**: Apply specific forces (not just positions)

**Method**:
- Measure applied forces (force sensors)
- Adjust motor commands to achieve desired forces
- Essential for manipulation and contact tasks

**Good For**: Grasping objects, pushing, pulling, assembly

**Example**: Picking up an egg requires force control—too little force and you drop it, too much and you crush it

### Compliance Control

**Goal**: Allow the robot to "give" when it contacts objects

**Method**:
- Make joints somewhat soft/flexible
- Absorb impacts safely
- Adapt to variable environments

**Good For**: Safe human-robot interaction, walking on uneven terrain

**Example**: A compliant robot arm can be safely pushed aside by a human, while a stiff arm could injure someone

### Model-Based Control

**Goal**: Use mathematical model of robot dynamics to predict and control behavior

**Method**:
- Model robot as a physical system (mass, inertia, friction)
- Calculate required torques to achieve desired accelerations
- Account for gravity, momentum, interaction forces

**Good For**: Dynamic movements, high-speed operation, complex tasks

**Limitations**: Requires accurate model, computationally expensive

This is the state of the art for advanced humanoid robots.

## Putting It Together: A Walking Robot

Let's walk through (pun intended) what happens when a humanoid robot takes a single step:

**Phase 1: Weight Shift**
- **Goal**: Transfer weight to right leg
- **Control**: Hip motors shift CoM over right foot
- **Sensing**: Force sensors in feet verify weight transfer
- **Balance**: IMU confirms robot is stable

**Phase 2: Swing Initiation**
- **Goal**: Lift left foot off ground
- **Control**: Hip and knee motors flex left leg
- **Sensing**: Force sensors confirm left foot has zero load
- **Balance**: CoM maintained over right foot

**Phase 3: Swing Phase**
- **Goal**: Move left leg forward
- **Control**: Coordinated hip, knee, ankle movements
- **Sensing**: Joint encoders track leg position
- **Balance**: Continuous IMU monitoring, small right ankle adjustments

**Phase 4: Foot Placement**
- **Goal**: Place left foot on ground ahead of robot
- **Control**: Extend leg to planned position, prepare for impact
- **Sensing**: Vision or LIDAR ensures clear landing spot
- **Timing**: Critical—must land when CoM is in right position

**Phase 5: Weight Transfer**
- **Goal**: Shift weight to newly planted left foot
- **Control**: Hip motors shift CoM forward and left
- **Sensing**: Force sensors verify new weight distribution
- **Balance**: Robot now balanced on left foot, ready to repeat with right leg

**Throughout**: IMU continuously monitors balance, motors make micro-adjustments, vision tracks environment, control system predicts and corrects.

This entire sequence happens in about 0.5-1 second for a human-like walking pace. The robot's control loop is running at 100-1000 Hz, making hundreds of tiny corrections during each step.

## Summary

**Actuators** convert electrical signals into physical motion, with **electric motors** providing precise control, **hydraulics** offering high power, and **pneumatics** providing compliant forces.

**Locomotion** in humanoid robots is challenging because walking requires dynamic balance—constantly shifting weight, lifting feet, and maintaining the center of mass within the support polygon.

**Balance** can be **static** (always stable) or **dynamic** (balanced through active control), with robots using **ankle**, **hip**, and **stepping strategies** to handle disturbances.

**Control systems** range from simple **position control** (move to angle) to sophisticated **model-based control** (predict dynamics and forces), with **force control** and **compliance** being critical for safe interaction.

**Walking** involves coordinated phases—weight shift, swing initiation, swing phase, foot placement, and weight transfer—all requiring precise sensing, control, and balance management at high frequencies.

Even a single step requires coordination of dozens of motors, integration of multiple sensors, continuous balance monitoring, and hundreds of control decisions per second—illustrating the complexity of embodied intelligence.

## Further Reading

- Full, R. J., & Koditschek, D. E. (1999). "Templates and anchors: neuromechanical hypotheses of legged locomotion on land." *Journal of Experimental Biology*, 202(23), 3325-3332.
- Kajita, S., et al. (2014). *Introduction to Humanoid Robotics*. Springer.
- Siciliano, B., & Khatib, O. (Eds.). (2016). *Springer Handbook of Robotics* (Chapters on Motion Control). Springer.

## Next Steps

Now that you understand how robots move and maintain balance, continue to [Week 4: Perception Pipeline](./week-04-perception) to explore how robots process sensor data to understand their environment.
