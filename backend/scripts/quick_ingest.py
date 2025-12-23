#!/usr/bin/env python3
"""
Quick ingestion script to add sample book content to Qdrant
"""
import os
import sys
import uuid
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere

# Load environment
load_dotenv()

# Sample book content about Physical AI and Robotics
SAMPLE_CHUNKS = [
    {
        "chapter": "1",
        "section": "Introduction to Physical AI",
        "page": 15,
        "content": """Physical AI refers to artificial intelligence systems that interact with the physical world through sensors, actuators, and embodied learning. Unlike traditional AI that operates purely in the digital domain, Physical AI must understand and navigate real-world environments, handle uncertainties, and adapt to dynamic conditions. This field combines computer vision, robotics, machine learning, and control theory to create intelligent systems that can perceive, reason about, and manipulate their surroundings."""
    },
    {
        "chapter": "1",
        "section": "History of Robotics",
        "page": 22,
        "content": """The history of robotics dates back to ancient automata, but modern robotics began in the 1950s with the development of programmable industrial robots. Key milestones include Unimate, the first industrial robot installed in 1961, and the development of computer-controlled manipulators at Stanford and MIT in the 1960s. The field has evolved from simple repetitive tasks to sophisticated autonomous systems capable of learning and adaptation."""
    },
    {
        "chapter": "2",
        "section": "Humanoid Robotics Fundamentals",
        "page": 45,
        "content": """Humanoid robots are designed to mimic human form and behavior, typically featuring a torso, head, two arms, and two legs. The humanoid form factor enables these robots to operate in human-designed environments and use tools created for humans. Key challenges include bipedal locomotion, dexterous manipulation, natural human-robot interaction, and achieving balance and stability while performing complex tasks."""
    },
    {
        "chapter": "2",
        "section": "Degrees of Freedom",
        "page": 52,
        "content": """Degrees of freedom (DOF) in robotics refer to the number of independent parameters that define the configuration of a robotic system. Human arms have approximately 7 DOF, allowing for highly dexterous manipulation. Humanoid robots typically implement 20-40 DOF to achieve human-like motion capabilities, with considerations for joint limits, workspace reachability, and redundancy for obstacle avoidance."""
    },
    {
        "chapter": "3",
        "section": "Perception Systems",
        "page": 78,
        "content": """Perception systems enable robots to understand their environment using various sensors. Vision systems use cameras and deep learning for object recognition, semantic segmentation, and scene understanding. LiDAR provides 3D spatial mapping, while force/torque sensors enable tactile perception. Multi-modal sensor fusion combines these inputs to create robust environmental representations for decision-making and control."""
    },
    {
        "chapter": "3",
        "section": "Computer Vision for Robotics",
        "page": 89,
        "content": """Computer vision in robotics involves processing visual information to extract meaningful representations for robot control. Modern approaches use convolutional neural networks (CNNs) for object detection, pose estimation, and visual servoing. Vision transformers are increasingly used for scene understanding and manipulation planning. Real-time performance is critical, requiring optimized models that can run at 30+ FPS on embedded hardware."""
    },
    {
        "chapter": "4",
        "section": "Motion Planning",
        "page": 112,
        "content": """Motion planning involves computing collision-free trajectories from start to goal configurations. Classical approaches include sampling-based methods like RRT (Rapidly-exploring Random Trees) and PRM (Probabilistic Roadmaps). Modern learning-based approaches use neural networks to predict feasible motions, combining the reliability of classical methods with the efficiency of learned models. Real-world applications require handling dynamic obstacles and uncertainties."""
    },
    {
        "chapter": "4",
        "section": "Control Theory",
        "page": 125,
        "content": """Robot control systems translate high-level commands into low-level actuator signals. PID controllers provide simple but effective control for many applications. Model predictive control (MPC) optimizes control sequences over finite horizons, enabling constraint handling and optimal performance. Modern approaches integrate learning-based controllers that adapt to system dynamics and environmental changes through experience."""
    },
    {
        "chapter": "5",
        "section": "Machine Learning for Robotics",
        "page": 156,
        "content": """Machine learning enables robots to improve performance through experience. Reinforcement learning allows robots to learn complex behaviors through trial and error, with recent successes in manipulation, locomotion, and navigation tasks. Imitation learning leverages human demonstrations to bootstrap learning. Transfer learning and sim-to-real techniques help bridge the reality gap between simulation and physical deployment."""
    },
    {
        "chapter": "5",
        "section": "Deep Reinforcement Learning",
        "page": 178,
        "content": """Deep reinforcement learning combines deep neural networks with reinforcement learning to learn control policies directly from high-dimensional sensory inputs. Algorithms like PPO (Proximal Policy Optimization), SAC (Soft Actor-Critic), and TD3 (Twin Delayed DDPG) have shown success in robotic tasks. Challenges include sample efficiency, sim-to-real transfer, safety during exploration, and learning from sparse rewards."""
    }
]

def main():
    print("🚀 Starting quick ingestion...")

    # Get credentials from environment
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_chunks")

    if not all([qdrant_url, qdrant_api_key, cohere_api_key]):
        print("❌ Error: Missing environment variables")
        return 1

    # Initialize clients
    print("📡 Connecting to Qdrant...")
    qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    print("🧠 Initializing Cohere...")
    cohere_client = cohere.Client(cohere_api_key)

    # Create collection
    print(f"📦 Creating collection '{collection_name}'...")
    try:
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1024,  # Cohere embed-english-v3.0 dimension
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Collection '{collection_name}' created!")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Collection '{collection_name}' already exists")
        else:
            print(f"⚠️  Warning: {e}")

    # Generate embeddings for all chunks
    print(f"\n🔢 Generating embeddings for {len(SAMPLE_CHUNKS)} chunks...")
    texts = [chunk["content"] for chunk in SAMPLE_CHUNKS]

    response = cohere_client.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )
    embeddings = response.embeddings
    print(f"✅ Generated {len(embeddings)} embeddings (dimension: {len(embeddings[0])})")

    # Prepare points for upsert
    print("\n💾 Uploading chunks to Qdrant...")
    points = []
    for i, (chunk, embedding) in enumerate(zip(SAMPLE_CHUNKS, embeddings)):
        point = models.PointStruct(
            id=str(uuid.uuid4()),  # Use UUID for point ID
            vector=embedding,
            payload={
                "content": chunk["content"],
                "chapter": chunk["chapter"],
                "section": chunk["section"],
                "page": chunk["page"],
                "source_document": "Physical AI & Humanoid Robotics Textbook"
            }
        )
        points.append(point)

    # Upsert to Qdrant
    qdrant.upsert(
        collection_name=collection_name,
        points=points
    )

    print(f"✅ Successfully uploaded {len(points)} chunks!")

    # Verify
    print("\n🔍 Verifying ingestion...")
    collection_info = qdrant.get_collection(collection_name)
    print(f"✅ Collection has {collection_info.points_count} points")

    print("\n🎉 Quick ingestion complete!")
    print(f"\n📊 Summary:")
    print(f"   - Collection: {collection_name}")
    print(f"   - Chunks ingested: {len(points)}")
    print(f"   - Chapters covered: 1-5")
    print(f"   - Topics: Physical AI, Humanoid Robotics, Perception, Control, ML")

    return 0

if __name__ == "__main__":
    sys.exit(main())
