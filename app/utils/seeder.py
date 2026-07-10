import random
from datetime import datetime, date, time, timedelta
from app.models import db
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.destination import Destination
from app.models.trip import Trip
from app.models.fuel import Fuel
from app.models.maintenance import Maintenance
from app.models.expense import Expense
from app.models.income import Income
from app.models.notification import Notification

# Geographic Center for Plot (Vavoshi) Loading yard, Raigad, Maharashtra
MINE_LAT = 18.8267
MINE_LNG = 73.1895

def seed_database():
    # 1. Seed Users (clear first to prevent duplicates)
    if User.query.count() == 0:
        admin = User(username="EkviraTransport", email="admin@ekviratransport.com", role="Admin")
        admin.set_password("Ekviratransport@3230")
        db.session.add(admin)
        
        manager = User(username="manager", email="manager@ekviratransport.com", role="Manager")
        manager.set_password("manager123")
        db.session.add(manager)
        db.session.commit()
        print("Users seeded.")

    # 2. Seed Destinations (Maharashtra specific Vavoshi routes)
    dest_data = [
        {"name": "Taloja", "distance": 35.0, "rate_per_ton": 425.0, "estimated_time": 1.0},
        {"name": "Roha", "distance": 85.0, "rate_per_ton": 620.0, "estimated_time": 2.5},
        {"name": "Khopoli", "distance": 20.0, "rate_per_ton": 150.0, "estimated_time": 0.6},
        {"name": "Karanje", "distance": 40.0, "rate_per_ton": 300.0, "estimated_time": 1.2},
        {"name": "Rasayani", "distance": 15.0, "rate_per_ton": 195.0, "estimated_time": 0.5},
        {"name": "Mahadhan", "distance": 65.0, "rate_per_ton": 420.0, "estimated_time": 2.0},
        {"name": "Alana", "distance": 30.0, "rate_per_ton": 170.0, "estimated_time": 0.8}
    ]
    
    destinations = []
    for d in dest_data:
        existing = Destination.query.filter_by(name=d["name"]).first()
        if not existing:
            dest = Destination(**d)
            db.session.add(dest)
            destinations.append(dest)
        else:
            destinations.append(existing)
    db.session.commit()
    print("Destinations seeded.")

    # 3. Seed Drivers (7 specified names)
    driver_names = [
        "manish gupta", "sahil jadhav", "pandhari bhoir", "sarang patil", 
        "jayesh pawar", "umesh rai", "kshitij thombre"
    ]
    
    drivers = []
    today = date.today()
    for i, name in enumerate(driver_names):
        # Format name properly (capitalize)
        formatted_name = name.title()
        lic_num = f"MH-46-{202500 + i}DL"
        existing = Driver.query.filter_by(license_number=lic_num).first()
        if not existing:
            aadhaar = f"99887766550{i}"
            joining = today - timedelta(days=random.randint(180, 365))
            lic_expiry = today + timedelta(days=random.randint(-10, 500))
            drv = Driver(
                name=formatted_name,
                mobile=f"913746280{i}",
                license_number=lic_num,
                license_expiry=lic_expiry,
                address=f"Driver Quarter Room #{i+1}, Vavoshi Yard, Raigad, Maharashtra",
                aadhaar_number=aadhaar,
                joining_date=joining,
                salary=24000 + (i * 400), # Rs 24,000 to 26,400
                status="Active"
            )
            db.session.add(drv)
            drivers.append(drv)
        else:
            drivers.append(existing)
    db.session.commit()
    print("Drivers seeded.")

    # 4. Seed Vehicles (7 specified MH numbers)
    veh_numbers = [
        "MH03CP5199", "MH46BE3230", "MH46BF7694", "MH46CL1115", 
        "MH46BP7191", "MH43BK2758", "MH43CE6357"
    ]
    vehicle_brands = ["Tata Signa 2823.K", "BharatBenz 2823C", "Ashok Leyland U-3520", "Tata Prima 3525.K"]
    vehicles = []
    for i, veh_num in enumerate(veh_numbers):
        existing = Vehicle.query.filter_by(vehicle_number=veh_num).first()
        if not existing:
            # Capacity 28 to 35 tons (tippers carry min 25 tons)
            capacity = float(random.choice([28.0, 30.0, 32.0, 35.0]))
            ins_expiry = today + timedelta(days=random.choice([-5, 12, 45, 120, 240]))
            fit_expiry = today + timedelta(days=random.choice([-1, 8, 30, 90, 180]))
            puc_expiry = today + timedelta(days=random.choice([-15, 15, 60, 150, 300]))
            
            # Simulated coordinate offsets near Vavoshi
            lat = MINE_LAT + (random.random() - 0.5) * 0.05
            lng = MINE_LNG + (random.random() - 0.5) * 0.05
            
            veh = Vehicle(
                vehicle_number=veh_num,
                vehicle_name=random.choice(vehicle_brands),
                model=str(random.choice([2022, 2023, 2024])),
                registration_number=f"RC-MH46-{98765 - i}",
                capacity=capacity,
                insurance_date=ins_expiry,
                fitness_date=fit_expiry,
                puc_date=puc_expiry,
                status="Idle",
                current_latitude=lat,
                current_longitude=lng,
                odometer=62000.0 + (i * 9000.0),
                fuel_type="Diesel",
                driver_id=drivers[i].id
            )
            db.session.add(veh)
            vehicles.append(veh)
        else:
            vehicles.append(existing)
    db.session.commit()

    # Link drivers back to vehicles
    for i, v in enumerate(vehicles):
        d = drivers[i]
        d.vehicle_id = v.id
    db.session.commit()
    print("Vehicles and Driver mappings seeded.")

    # 5. Seed fuel logs, Maintenance, and Trips historically
    if Trip.query.count() == 0:
        print("Generating historical operations data...")
        start_date = today - timedelta(days=300)
        
        # Seed fuel refills
        for v in vehicles:
            odometer_acc = float(v.odometer) - 12000.0
            refill_date = start_date
            
            while refill_date < today:
                refill_date += timedelta(days=random.randint(4, 7))
                if refill_date >= today:
                    break
                
                fuel_qty = float(random.randint(120, 180)) # liters
                price = float(random.choice([92.8, 93.5, 94.2]))
                
                # Each tipper has a minimum average of 2 km/l (Range: 2.0 - 3.1 km/l)
                eff_mileage = float(round(random.uniform(2.0, 3.1), 2))
                odometer_acc += fuel_qty * eff_mileage
                
                f_log = Fuel(
                    vehicle_id=v.id,
                    date=refill_date,
                    fuel_filled=fuel_qty,
                    price=price,
                    mileage=eff_mileage,
                    fuel_station=random.choice(["Indian Oil (Panvel)", "HP Pump (Rasayani)", "BPCL Pen Services", "Shell Highway (Khopoli)"])
                )
                db.session.add(f_log)
                
                # Create corresponding Fuel Expense
                exp = Expense(
                    category="Diesel",
                    amount=fuel_qty * price,
                    date=refill_date,
                    description=f"Refueled {fuel_qty}L at {f_log.fuel_station}",
                    vehicle_id=v.id
                )
                db.session.add(exp)
            
            # Sync final odometer
            v.odometer = odometer_acc
            
            # Seed Maintenance events (3-4 events per truck over the year)
            maint_date = start_date + timedelta(days=random.randint(15, 60))
            while maint_date < today:
                next_m = maint_date + timedelta(days=random.randint(60, 90))
                cost = float(random.randint(5000, 32000))
                tc = random.choice([True, False, False])
                oc = True
                bc = random.choice([True, False, False, False])
                
                m_log = Maintenance(
                    vehicle_id=v.id,
                    service_date=maint_date,
                    next_service_date=next_m,
                    tyre_change=tc,
                    oil_change=oc,
                    battery_change=bc,
                    service_cost=cost,
                    workshop_name=random.choice(["Pen Auto Services", "Tata Motors Authorized (Panvel)", "Raigad Tipper Garage", "Highway Mechanics"]),
                    details=f"Routine service. Oil: {oc}, Tyre: {tc}, Battery: {bc}."
                )
                db.session.add(m_log)
                db.session.commit()
                
                # Create Maintenance Expense
                exp = Expense(
                    category="Maintenance" if not tc else "Repair",
                    amount=cost,
                    date=maint_date,
                    description=f"Scheduled service at {m_log.workshop_name}",
                    vehicle_id=v.id,
                    maintenance_id=m_log.id
                )
                db.session.add(exp)
                
                maint_date = next_m + timedelta(days=random.randint(10, 20))
        
        # Seed monthly driver salary expenses
        salary_date = start_date
        while salary_date < today:
            salary_date = date(salary_date.year, salary_date.month, 5)
            if salary_date >= today:
                break
                
            for d in drivers:
                exp = Expense(
                    category="Driver Salary",
                    amount=float(d.salary),
                    date=salary_date,
                    description=f"Monthly salary payment to driver {d.name}"
                )
                db.session.add(exp)
                
            if salary_date.month == 12:
                salary_date = date(salary_date.year + 1, 1, 1)
            else:
                salary_date = date(salary_date.year, salary_date.month + 1, 1)

        # Seed Trips (about 15-20 trips per vehicle historically)
        for v in vehicles:
            d_drv = Driver.query.get(v.driver_id)
            trip_date = start_date + timedelta(days=random.randint(1, 10))
            
            while trip_date < today - timedelta(days=2):
                dest = random.choice(destinations)
                # Enforce: min weight carried is 25 tons
                coal_wt = float(round(random.uniform(25.0, float(v.capacity)), 2))
                
                # Freight Income: weight * rate
                freight = coal_wt * float(dest.rate_per_ton)
                
                # Expected diesel consumption (min 2 km/l average)
                mileage_factor = random.uniform(2.0, 2.8)
                diesel_req = float(dest.distance) * 2 / mileage_factor
                diesel_cost = diesel_req * 94.0
                
                toll = float(random.choice([150, 250, 300]))
                misc = float(random.randint(100, 300))
                
                st_time = time(random.randint(6, 12), random.choice([0, 15, 30, 45]))
                duration_hours = float(dest.estimated_time) + random.uniform(-0.1, 0.4)
                
                et_time_dt = datetime.combine(trip_date, st_time) + timedelta(hours=duration_hours)
                end_d = et_time_dt.date()
                end_t = et_time_dt.time()
                
                trip = Trip(
                    vehicle_id=v.id,
                    driver_id=d_drv.id,
                    destination_id=dest.id,
                    source="Plot (Vavoshi)",
                    coal_weight=coal_wt,
                    start_date=trip_date,
                    start_time=st_time,
                    end_date=end_d,
                    end_time=end_t,
                    status="Delivered",
                    freight_amount=freight,
                    diesel_used=diesel_req,
                    toll_cost=toll,
                    misc_expense=misc
                )
                trip.calculate_profit(fuel_price=94.0)
                db.session.add(trip)
                db.session.commit()
                
                # Income logging
                inc = Income(
                    category="Freight Charges",
                    amount=freight,
                    date=end_d,
                    description=f"Freight charge for trip #{trip.id} to {dest.name}",
                    trip_id=trip.id
                )
                db.session.add(inc)
                
                # Expenses logging
                db.session.add(Expense(category="Diesel", amount=diesel_cost, date=trip_date, description=f"Diesel for trip #{trip.id}", vehicle_id=v.id, trip_id=trip.id))
                db.session.add(Expense(category="Toll", amount=toll, date=trip_date, description=f"Tolls for trip #{trip.id}", vehicle_id=v.id, trip_id=trip.id))
                db.session.add(Expense(category="Miscellaneous", amount=misc, date=trip_date, description=f"Misc expenses for trip #{trip.id}", vehicle_id=v.id, trip_id=trip.id))
                
                trip_date += timedelta(days=random.randint(5, 10))

        # Seed Active Trips near Navi Mumbai (Running/Loading now)
        # Vehicle 3 (MH46BF7694) - Running to Taloja
        v3 = vehicles[2]
        d3 = Driver.query.get(v3.driver_id)
        v3.status = "Active"
        d3.status = "On Trip"
        t3 = Trip(
            vehicle_id=v3.id, driver_id=d3.id, destination_id=destinations[0].id, # Taloja
            coal_weight=27.5, start_date=today, start_time=time(8, 0),
            status="Running", freight_amount=27.5 * float(destinations[0].rate_per_ton)
        )
        db.session.add(t3)
        
        # Vehicle 4 (MH46CL1115) - Running to Roha
        v4 = vehicles[3]
        d4 = Driver.query.get(v4.driver_id)
        v4.status = "Active"
        d4.status = "On Trip"
        t4 = Trip(
            vehicle_id=v4.id, driver_id=d4.id, destination_id=destinations[1].id, # Roha
            coal_weight=29.0, start_date=today, start_time=time(6, 30),
            status="Running", freight_amount=29.0 * float(destinations[1].rate_per_ton)
        )
        db.session.add(t4)
        
        # Vehicle 5 (MH46BP7191) - Loading to Khopoli
        v5 = vehicles[4]
        d5 = Driver.query.get(v5.driver_id)
        v5.status = "Active"
        d5.status = "On Trip"
        t5 = Trip(
            vehicle_id=v5.id, driver_id=d5.id, destination_id=destinations[2].id, # Khopoli
            coal_weight=26.0, start_date=today, start_time=time(9, 15),
            status="Loading", freight_amount=26.0 * float(destinations[2].rate_per_ton)
        )
        db.session.add(t5)
        
        # Vehicle 6 (MH43BK2758) - Under Maintenance
        v6 = vehicles[5]
        v6.status = "Maintenance"
        
        # Vehicle 7 (MH43CE6357) - Idle but has a breakdown notification
        v7 = vehicles[6]
        v7.status = "Idle"
        
        # Seed warnings notifications
        for drv in drivers:
            if drv.license_expiry <= today + timedelta(days=15):
                db.session.add(Notification(
                    driver_id=drv.id,
                    type="License Expiry",
                    message=f"License of driver {drv.name} ({drv.license_number}) expires on {drv.license_expiry}!"
                ))
        
        for veh in vehicles:
            if veh.insurance_date <= today + timedelta(days=15):
                db.session.add(Notification(
                    vehicle_id=veh.id,
                    type="Insurance Expiry",
                    message=f"Insurance for vehicle {veh.vehicle_number} expires on {veh.insurance_date}!"
                ))
            if veh.fitness_date <= today + timedelta(days=15):
                db.session.add(Notification(
                    vehicle_id=veh.id,
                    type="Fitness Expiry",
                    message=f"Fitness certificate for vehicle {veh.vehicle_number} expires on {veh.fitness_date}!"
                ))
            if veh.puc_date <= today + timedelta(days=15):
                db.session.add(Notification(
                    vehicle_id=veh.id,
                    type="PUC Expiry",
                    message=f"PUC certificate for vehicle {veh.vehicle_number} expires on {veh.puc_date}!"
                ))
                
        # Low fuel warnings
        db.session.add(Notification(
            vehicle_id=vehicles[0].id,
            type="Low Fuel",
            message=f"Vehicle {vehicles[0].vehicle_number} is reporting low fuel level (under 15%)."
        ))
        
        # Breakdown notifications
        db.session.add(Notification(
            vehicle_id=v7.id,
            type="Breakdown",
            message=f"Breakdown reported: Vehicle {v7.vehicle_number} electrical/battery issue near Panvel bypass."
        ))

        db.session.commit()
        print("Historical and active operations data seeded.")
