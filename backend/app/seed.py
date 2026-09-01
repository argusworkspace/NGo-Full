"""Development seed data. Do NOT run against a production database.

Creates:
  - admin@gmail.com / admin123 (ADMIN)
  - user@example.com  / User@123  (VOLUNTEER)
  - one sample project, published, with one question of each supported type

Usage: python -m app.seed
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.modules.auth.models import User
from app.modules.surveys.models import Project

SAMPLE_QUESTIONS = [
    {"id": "q1", "question": "What is the name of the school?", "type": "text", "required": True},
    {"id": "q2", "question": "Number of students in the school?", "type": "number", "required": True},
    {"id": "q3", "question": "Date of the survey visit", "type": "date", "required": False},
    {
        "id": "q4",
        "question": "What is the gender of the student?",
        "type": "single_choice",
        "required": True,
        "options": [
            {"id": "opt1", "label": "Male"},
            {"id": "opt2", "label": "Female"},
            {"id": "opt3", "label": "Other"},
        ],
    },
    {
        "id": "q5",
        "question": "Which facilities are available?",
        "type": "multiple_choice",
        "required": False,
        "options": [
            {"id": "opt1", "label": "Library"},
            {"id": "opt2", "label": "Laboratory"},
            {"id": "opt3", "label": "Sports"},
        ],
    },
    {"id": "q6", "question": "Does the school have a library?", "type": "boolean", "required": True},
    {"id": "q7", "question": "Any additional remarks?", "type": "textarea", "required": False},
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@gmail.com"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@gmail.com",
                hashed_password=hash_password("admin123"),
                role="ADMIN",
            )
            db.add(admin)
            await db.flush()
            print("Created admin@gmail.com")
        else:
            print("admin@gmail.com already exists, skipping")

        result = await db.execute(select(User).where(User.email == "user@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                name="Field User",
                email="user@example.com",
                hashed_password=hash_password("User@123"),
                role="VOLUNTEER",
            )
            db.add(user)
            await db.flush()
            print("Created user@example.com")
        else:
            print("user@example.com already exists, skipping")

        result = await db.execute(select(Project).where(Project.name == "School Health Survey 2026"))
        project = result.scalar_one_or_none()
        if not project:
            project = Project(
                name="School Health Survey 2026",
                description="Sample survey conducted across government schools",
                questions=SAMPLE_QUESTIONS,
                status="PUBLISHED",
                created_by=admin.id,
            )
            db.add(project)
            await db.flush()
            print("Created sample project 'School Health Survey 2026'")
        else:
            print("Sample project already exists, skipping")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
    print("\nSeed complete. Dev credentials (CHANGE/REMOVE before production):")
    print("  ADMIN: admin@gmail.com / admin123")
    print("  VOLUNTEER: user@example.com / User@123")
