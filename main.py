"""
SmartScheduler - AI-Powered Appointment Booking System
FastAPI Backend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(
    title="SmartScheduler API",
    description="AI-powered appointment booking system",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Customer(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class Appointment(BaseModel):
    customer: Customer
    service: str
    start_time: datetime
    duration_minutes: int = 60
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    customer: Customer
    service: str
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime

class AvailabilitySlot(BaseModel):
    start_time: datetime
    end_time: datetime
    available: bool

# In-memory storage (replace with database in production)
appointments_db = {}
services_db = {
    "consultation": {"name": "Initial Consultation", "duration": 60, "price": 100},
    "followup": {"name": "Follow-up Visit", "duration": 30, "price": 50},
    "treatment": {"name": "Treatment Session", "duration": 90, "price": 150},
}

# Health check
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "SmartScheduler API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Get available services
@app.get("/api/services")
async def get_services():
    """Get list of available services"""
    return {"services": services_db}

# Get available time slots
@app.get("/api/availability", response_model=List[AvailabilitySlot])
async def get_availability(date: str, service: str):
    """
    Get available time slots for a specific date and service

    AI will optimize these based on:
    - Existing appointments
    - Staff availability
    - Historical booking patterns
    - Buffer times
    """
    # Parse date
    try:
        target_date = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")

    # Get service duration
    if service not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    duration = services_db[service]["duration"]

    # Generate available slots (9 AM - 5 PM, every 30 minutes)
    slots = []
    current_time = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=17, minute=0, second=0, microsecond=0)

    while current_time < end_of_day:
        # Check if slot is available (not booked)
        slot_end = current_time + timedelta(minutes=duration)
        is_available = not any(
            appt["start_time"] < slot_end and appt["end_time"] > current_time
            for appt in appointments_db.values()
        )

        slots.append(AvailabilitySlot(
            start_time=current_time,
            end_time=slot_end,
            available=is_available
        ))

        current_time += timedelta(minutes=30)

    return slots

# Book appointment
@app.post("/api/appointments", response_model=AppointmentResponse)
async def book_appointment(appointment: Appointment):
    """
    Book a new appointment

    AI features:
    - Conflict detection
    - Optimal time suggestion
    - Customer preference learning
    """
    # Validate service exists
    if appointment.service not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")

    # Calculate end time
    end_time = appointment.start_time + timedelta(minutes=appointment.duration_minutes)

    # Check for conflicts
    for appt in appointments_db.values():
        if (appointment.start_time < appt["end_time"] and
            end_time > appt["start_time"]):
            raise HTTPException(
                status_code=409,
                detail="Time slot not available. Please choose another time."
            )

    # Create appointment
    appt_id = f"appt_{len(appointments_db) + 1}"
    new_appointment = {
        "id": appt_id,
        "customer": appointment.customer.model_dump(),
        "service": appointment.service,
        "start_time": appointment.start_time,
        "end_time": end_time,
        "status": "confirmed",
        "created_at": datetime.now(),
        "notes": appointment.notes
    }

    appointments_db[appt_id] = new_appointment

    # TODO: In production:
    # - Send confirmation email
    # - Send SMS reminder
    # - Add to staff calendar
    # - Trigger AI optimization

    return AppointmentResponse(**new_appointment)

# Get appointments
@app.get("/api/appointments")
async def get_appointments(
    date: Optional[str] = None,
    customer_email: Optional[str] = None
):
    """Get appointments with optional filters"""
    results = list(appointments_db.values())

    # Filter by date if provided
    if date:
        target_date = datetime.fromisoformat(date).date()
        results = [
            appt for appt in results
            if appt["start_time"].date() == target_date
        ]

    # Filter by customer email if provided
    if customer_email:
        results = [
            appt for appt in results
            if appt["customer"]["email"] == customer_email
        ]

    return {"appointments": results, "count": len(results)}

# Cancel appointment
@app.delete("/api/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment"""
    if appointment_id not in appointments_db:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointments_db[appointment_id]["status"] = "cancelled"

    # TODO: In production:
    # - Send cancellation confirmation
    # - Add to waitlist if applicable
    # - Update AI optimization

    return {
        "message": "Appointment cancelled successfully",
        "appointment_id": appointment_id
    }

# AI-powered insights endpoint
@app.get("/api/insights")
async def get_insights():
    """
    AI-powered business insights

    In production, this would analyze:
    - Booking patterns
    - Peak times
    - Customer retention
    - Revenue optimization
    - Staff utilization
    """
    total_appointments = len(appointments_db)
    confirmed = sum(1 for appt in appointments_db.values() if appt["status"] == "confirmed")
    cancelled = sum(1 for appt in appointments_db.values() if appt["status"] == "cancelled")

    return {
        "total_appointments": total_appointments,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "cancellation_rate": (cancelled / total_appointments * 100) if total_appointments > 0 else 0,
        "insights": [
            "Your peak booking time is 2-4 PM",
            "Consider adding a waitlist feature",
            "Tuesday and Thursday are your busiest days"
        ]
    }

if __name__ == "__main__":
    print("🗓️  SmartScheduler API Starting...")
    print("📍 API Docs: http://localhost:8000/docs")
    print("🚀 Ready to accept bookings!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
