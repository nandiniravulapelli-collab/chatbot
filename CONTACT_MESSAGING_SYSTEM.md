# Contact and Messaging System Implementation

## Overview
Implemented a complete contact and messaging system where:
- Admins can edit contact details displayed to students
- Students can send messages to admins via the contact page
- Admins can view all student messages and optionally reply
- Students can view their sent messages and admin replies
- Removed the "Send us a Message" form from admin contact page

## Changes Made

### 1. Backend API Endpoints (app.py)

#### New Collections Added
- `contact_details` - Stores editable contact information
- `student_messages` - Stores student messages and admin replies

#### New API Endpoints

**Contact Details (Public):**
- `GET /api/contact-details` - Get current contact details
- `PUT /api/admin/contact-details` - Update contact details (admin only)

**Student Messages:**
- `POST /api/student-messages` - Send a message to admin (student only)
- `GET /api/admin/student-messages` - View all student messages (admin only)
- `PUT /api/admin/student-messages/<id>/reply` - Reply to a student message (admin only)
- `GET /api/student-messages` - View own messages (student only)

### 2. Frontend Changes

#### Contact Page (templates/contact.html)
- **Removed**: Name and email fields from message form (auto-filled from session)
- **Added**: Dynamic loading of contact details from MongoDB
- **Added**: JavaScript to load contact details on page load
- **Added**: Message submission via API to `/api/student-messages`
- **Modified**: Contact info cards now display data from database instead of hardcoded values

#### Admin Dashboard (templates/admin.html)
- **Added**: "Contact Details" sidebar menu item
- **Added**: "Student Messages" sidebar menu item
- **Added**: Contact Details section with editable form (address, phone, email, office hours)
- **Added**: Student Messages section with table showing all messages
- **Added**: Reply functionality for pending messages
- **Added**: View reply functionality for replied messages
- **Added**: JavaScript functions:
  - `loadContactDetails()` - Load current contact details
  - `loadStudentMessages()` - Load all student messages
  - `replyToMessage()` - Send reply to student
  - `viewReply()` - View existing reply

#### Student Dashboard (templates/dashboard.html)
- **Added**: "My Messages" sidebar menu item
- **Added**: `openMyMessagesModal()` function to display student's messages
- **Added**: Modal showing all sent messages with admin replies
- **Added**: Status badges (pending/replied) for each message
- **Added**: Display of admin replies in highlighted boxes

### 3. Database Schema

#### contact_details Collection
```json
{
  "_id": ObjectId,
  "address": "University Campus\nEducation Road, Main Building\nCity - 560001",
  "phone": "Toll Free: 1800-123-4567\nOffice: +91 80 2345 6789\nFax: +91 80 2345 6790",
  "email": "General: info@university.edu\nAdmissions: admit@university.edu\nSupport: help@university.edu",
  "office_hours": "Monday - Friday: 9:00 AM - 5:00 PM\nSaturday: 9:00 AM - 1:00 PM\nSunday: Closed"
}
```

#### student_messages Collection
```json
{
  "_id": ObjectId,
  "student_id": "student_user_id",
  "student_name": "Student Name",
  "student_email": "student@email.com",
  "subject": "General Inquiry",
  "message": "Message content",
  "reply": null or "Admin reply content",
  "status": "pending" or "replied",
  "created_at": ISODate,
  "replied_at": ISODate or null
}
```

## How It Works

### For Admins

1. **Edit Contact Details:**
   - Go to Admin Dashboard → Contact Details
   - Edit address, phone, email, and office hours
   - Click "Save Contact Details"
   - Changes are immediately reflected on the student contact page

2. **View Student Messages:**
   - Go to Admin Dashboard → Student Messages
   - See all messages from students with status (pending/replied)
   - View student name, email, subject, message, and date

3. **Reply to Messages (Optional):**
   - Click "Reply" button on pending messages
   - Enter reply in the prompt
   - Message status changes to "replied"
   - Student can view the reply in their "My Messages" section

### For Students

1. **Send Message:**
   - Go to Support/Contact page
   - Select subject and enter message
   - Click "Send Message"
   - Message is saved to database with "pending" status

2. **View Contact Details:**
   - Contact page displays current address, phone, email, office hours
   - Information is loaded from database (editable by admin)

3. **View Own Messages:**
   - Go to Student Dashboard → My Messages
   - See all sent messages with status
   - View admin replies (if any) in highlighted boxes
   - See when message was sent and when reply was received

## Security Features

- **Role-based access control**: All endpoints check user role
- **Session authentication**: Only authenticated users can access APIs
- **Admin-only operations**: Contact details editing and message replying restricted to admins
- **Student-only operations**: Sending messages and viewing own messages restricted to students
- **No data exposure**: Students can only see their own messages, not others'

## Testing Instructions

### Test Admin Contact Details Editing
1. Log in as admin
2. Go to "Contact Details" in sidebar
3. Edit any field (address, phone, email, office hours)
4. Click "Save Contact Details"
5. Log out and log in as student
6. Go to Support page - verify changes are visible

### Test Student Message Sending
1. Log in as student
2. Go to Support page
3. Fill in subject and message
4. Click "Send Message"
5. Verify success message
6. Go to "My Messages" in dashboard - verify message appears with "pending" status

### Test Admin Message Viewing and Replying
1. Log in as admin
2. Go to "Student Messages" in sidebar
3. Verify the student message appears
4. Click "Reply" button
5. Enter a reply
6. Verify message status changes to "replied"
7. Log out and log in as student
8. Go to "My Messages" - verify admin reply is visible

## Files Modified

1. `app.py` - Added API endpoints, new collections, ObjectId import
2. `templates/contact.html` - Dynamic contact details, message form integration
3. `templates/admin.html` - Contact details section, student messages section
4. `templates/dashboard.html` - My Messages modal

## Preserved Functionality

All existing features remain intact:
- MongoDB as source of truth
- Authentication system
- Role-based access control
- Fee structure and exam schedule viewing
- Chatbot functionality
- NLG integration
- Semantic matching
- Admin analytics
