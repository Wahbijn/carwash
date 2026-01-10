# Car Wash Booking System

![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A comprehensive Django-based web application for managing car wash services with integrated loyalty programs, gamification features, and automated customer engagement.

## Features

### Core Functionality
- **Service Management**: Manage multiple car wash services with customizable pricing and duration
- **Vehicle Registration**: Users can register multiple vehicles with make, model, and license plate details
- **Smart Booking System**: Book car wash services with date/time scheduling and real-time availability
- **Status Tracking**: Track bookings through multiple states (Pending, Confirmed, Cancelled, Done)
- **Automated Reminders**: Scheduled email notifications for upcoming appointments

### User Experience
- **Admin Dashboard**: Comprehensive admin panel for managing bookings, services, and users
- **User Dashboard**: Personalized dashboard for customers to view bookings and account details
- **Responsive Design**: Bootstrap 5-powered responsive interface for all devices

### Gamification & Loyalty

#### Loyalty Program
- **4 Tier System**: Bronze, Silver, Gold, and Platinum tiers
- **Points System**: Earn 1 point for every 10 TND spent on completed bookings
- **Rewards Catalog**: Redeemable rewards with 5 default options
- **Transaction History**: Track all points earned and spent
- **Visual Progress**: Beautiful gradient cards showing tier progress

#### Badges & Achievements
- **15 Default Achievements**: Unlock badges based on your activity
- **4 Rarity Levels**: Common, Rare, Epic, and Legendary badges
- **Achievement Categories**:
  - First Steps: Getting started achievements
  - VIP: Premium customer badges
  - Spending: Purchase milestone badges
  - Loyalty: Tier progression badges
- **Progress Tracking**: Visual progress bars showing unlock percentage
- **Badge Gallery**: Beautiful gallery with locked/unlocked visualization

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **Database**: PostgreSQL
- **Task Scheduling**: Django APScheduler for automated reminders
- **Authentication**: Django's built-in authentication system

### Frontend
- **UI Framework**: Bootstrap 5
- **Forms**: Django Crispy Forms with Bootstrap 5 integration
- **Icons & Styling**: Custom CSS with gradient designs

### Additional Libraries
- **Environment Management**: python-dotenv
- **Image Processing**: Pillow
- **HTTP Requests**: requests library

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Setup

1. **Clone the repository**
```bash
git clone <your-repository-url>
cd carwash
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Database configuration
DATABASE_NAME=carwash_db
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email configuration (for reminders)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## Project Structure

```
carwash/
├── accounts/              # User account management
├── badges/                # Gamification badges system
├── carwash_project/       # Main project settings
├── loyalty/               # Loyalty program and rewards
├── wash/                  # Core booking and service management
├── logs/                  # Application logs
├── check_jobs.py          # Scheduler monitoring utility
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in git)
```

## Usage

### Admin Access
1. Navigate to `http://127.0.0.1:8000/admin`
2. Log in with superuser credentials
3. Manage services, bookings, users, rewards, and badges

### User Features
1. **Register/Login**: Create an account or log in
2. **Add Vehicles**: Register your vehicles
3. **Book Services**: Select service, vehicle, and schedule
4. **Earn Points**: Complete bookings to earn loyalty points
5. **Unlock Badges**: Achieve milestones to unlock badges
6. **Redeem Rewards**: Use points to claim rewards

## Automated Features

### Booking Reminders
- Scheduled email reminders sent before appointments
- Customizable reminder timing
- Tracks reminder status to avoid duplicates

### Automatic Points Award
- Points automatically awarded when booking status changes to "Done"
- Calculation based on total booking price (10 TND = 1 point)

### Badge Unlocking
- Automatic badge unlocking based on user activity
- Real-time progress tracking
- Notification system for new achievements

## Development

### Check Scheduled Jobs
```bash
python check_jobs.py
```

### Run Tests
```bash
python manage.py test
```

### Monitoring
- Check logs in the `logs/` directory
- Monitor scheduler status using `check_jobs.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Author

Wahbi Jouini

## Support

For issues and questions, please open an issue on the GitHub repository.
