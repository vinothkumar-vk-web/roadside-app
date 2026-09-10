# Malumichampatti Hyperlocal Roadside Assistance MVP Backend

This codebase implements the core backend service for the **Malumichampatti, Coimbatore pilot launch** of a hyperlocal on-demand roadside assistance app (Mechanic, Towing, and Fuel Delivery Booking).

---

## 🚀 Quick Setup & Local Execution

### 1. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy asyncpg pydantic locust
```

### 2. Run the FastAPI Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive API Docs (Swagger): `http://localhost:8000/docs`

---

## 🛠 Features Implemented

1. **Partner Registration System Flow**:
   - `POST /api/v1/partners/register`: Registers partner with phone, photo/ID proof links, service types (`mechanic`, `towing`, `fuel_delivery`), base lat-long, live location toggle.
   - Initial status is `PENDING`.
   - `POST /api/v1/admin/partners/verify`: Admin approves partner before they can toggle online status.
   - `POST /api/v1/partners/{partner_id}/availability`: Toggles `is_online` status and updates location without external maps API overhead.

2. **4-Step Escalation State Machine**:
   - **Step 1**: High-priority FCM Push Notification with Accept/Reject action buttons.
   - **Step 2** (30-45s timeout): Automated Exotel voice call readout.
   - **Step 3** (Call timeout/failure): SMS fallback via MSG91/Twilio.
   - **Step 4**: Auto-reassign to the next-nearest available partner. Never leaves the customer waiting on an unresponsive mechanic.

3. **High Reliability & Performance Architecture**:
   - Zero external map calls on partner location updates (uses in-memory / Redis spatial cache).
   - Async non-blocking FastAPI handlers with PostgreSQL connection pooling (`asyncpg`).
   - Graceful degradation if SMS/Voice APIs encounter errors.

4. **Multi-City Routing Strategy**:
   - All partners and requests are linked to `ServiceZone`.
   - Pre-seeded with `zone_name="Malumichampatti"`. Expanding to future cities (e.g. Salem, Madurai) only requires adding a row to `service_zones`.

---

## 🧪 Load Testing with Locust
Run the Locust concurrent user simulation:
```bash
locust -f locustfile.py --host=http://localhost:8000
```
Open `http://localhost:8089` to start simulating 500+ concurrent customers and mechanics in Malumichampatti.
