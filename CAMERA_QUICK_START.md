# Camera Monitor - Quick Start Guide

## 🎬 Getting Started (2 Minutes)

### Prerequisites Check ✅
- ✅ Backend running on `http://localhost:5000` (mock server)
- ✅ Frontend running on `http://localhost:3001` (React app)
- ✅ WebSocket connection active
- ✅ Camera/webcam available on your computer

### Step-by-Step

#### 1. **Open Dashboard** (URL: `http://localhost:3001`)
```
You should see the admin dashboard with:
- "📹 Camera Monitor" button in the top navigation
- "📊 Dashboard" button showing current page
- Empty or existing flagged students list
```

#### 2. **Click "📹 Camera Monitor" Button**
```
Page should load showing:
✓ Camera View heading with status indicator
✓ Two buttons: "▶ Start Camera" and "🎯 Start Detection" (disabled)
✓ Black video placeholder area
✓ Detection info panels below
```

#### 3. **Click "▶ Start Camera" Button**
```
Browser will prompt for camera permission:
- Click "Allow" to grant camera access
- You should see live webcam feed in the canvas

Expected: Real-time video from your webcam visible
```

#### 4. **Click "🎯 Start Detection" Button**
```
System begins analyzing the video:
- You'll see bounding boxes appear around faces
- Each person gets a unique ID (STU_0001, STU_0002, etc.)
- Green boxes = looking forward (ethical)
- Yellow boxes = head turning (warning)
- Red boxes = head back (critical)
```

---

## 📊 Testing Offense Detection

### Test Scenario 1: Simple Head Turn
1. **Start camera and detection**
2. **Turn your head LEFT and keep it there for 4 seconds**
3. **Observe:**
   - Yellow box appears with "LEFT (⚠️)" label
   - Duration timer starts: "0.5s" → "1.0s" → "2.0s" → ...
   - At 3.0s: **"OFFENSE LOGGED"** appears
4. **Switch to Dashboard:**
   - Your student ID appears in flagged list
   - Offense count shows 1

### Test Scenario 2: Multiple Offenses → Auto Flagging
1. **Create 3 separate offenses** (each 3+ seconds):
   - First: Turn LEFT for 3.2 seconds → Logged (count: 1)
   - Second: Turn RIGHT for 3.1 seconds → Logged (count: 2)
   - Third: Turn BACK for 3.5 seconds → Logged (count: 3)
2. **Result:**
   - Dashboard shows: **Your ID | Offenses: 3 | Status: 🚨 FLAGGED**
   - Student card highlights in red

### Test Scenario 3: Dashboard Interaction
1. **View flagged student card**
2. **Click expand arrow** to see offense details
3. **Available actions:**
   - ⬜ **Reset**: Remove from flagged list (status → inactive)
   - 🗑️ **Clear All**: Delete all offense records
4. **Confirm actions:** Dashboard updates in real-time via WebSocket

---

## 🎯 What You'll See on Camera Monitor

### Video Canvas
```
┌─────────────────────────────────────┐
│ [Your Webcam Feed]                  │
│                                     │
│   ┌─────────────┐                   │
│   │ STU_0001    │ ← Bounding Box    │
│   │ LEFT (⚠️)   │ Duration: 3.2s    │
│   │ [Your Face] │                   │
│   └─────────────┘ (Yellow = Warning)│
│                                     │
└─────────────────────────────────────┘
```

### Detection Info Panel
```
🎯 Active Detections: 1 student detected

⚠️ Pose Indicators:
  ✓ Forward (Ethical)
  ⚠ Left/Right (Warning - 3s)
  🚨 Back (Critical - Offense)

⏱️ Pose Duration Tracking:
  STU_0001 | LEFT | 3.2s ← Turning left for 3.2 seconds
```

---

## 🧪 Mock Mode Testing (No Webcam Needed)

If you don't have a webcam or want to test without one:

1. **Backend will auto-detect missing packages**
2. **Falls back to mock detection mode**
3. **Simulates realistic student behavior:**
   - Random head poses (80% forward, 20% other)
   - Auto-generates offense after 3 seconds
   - Emits detection data every 0.5 seconds
4. **Use this to test dashboard functionality**

---

## 🔴 Troubleshooting

### Camera Won't Start
```
Symptom: Button shows "Start Camera" but nothing happens
Fix: 
  1. Check browser console (F12)
  2. Grant camera permission in browser settings
  3. Ensure no other app is using camera
  4. Refresh page (F5)
```

### Detection Button Disabled
```
Symptom: "Start Detection" button is grayed out
Fix:
  - First click "Start Camera" to enable it
  - Camera must be active before detection starts
```

### No Bounding Boxes Appear
```
Symptom: Camera shows but no person detection boxes
Fix:
  1. Ensure good lighting in room
  2. Face must be clearly visible to camera
  3. Position face 1-2 meters from camera
  4. Check backend logs for errors
```

### Dashboard Not Updating
```
Symptom: Offenses logged but dashboard shows old data
Fix:
  1. Refresh dashboard (F5)
  2. Check WebSocket connection status
  3. Verify backend and frontend are communicating
  4. Check browser console for errors
```

---

## 🎮 Interactive Features

### Real-Time Controls

**Camera Monitor Page:**
```
Button               State      Action
─────────────────────────────────────────────
▶ Start Camera      Active     Starts webcam stream
⏹ Stop Camera       Active     Stops webcam
─────────────────────────────────────────────
🎯 Start Detection  Ready      Activates vision pipeline
🛑 Stop Detection   Active     Stops analysis
```

**Dashboard Page:**
```
Action              Effect
───────────────────────────────────────
Click Student Card  Expands to show offense details
⬜ Reset Button     Removes from flagged list
🗑️ Clear All        Deletes all offenses for student
Refresh (F5)        Pulls latest data from backend
```

---

## 📈 Live Monitoring Example

```
Timeline of Events (Real-time monitoring):

12:30:00 - Camera started, student STU_0001 detected
12:30:05 - Student turns HEAD LEFT
12:30:08 - YELLOW box appears, duration: 2.8s ⚠️
12:30:10 - Duration: 3.0s - OFFENSE #1 LOGGED 🚨
           [WebSocket emits student_flagged event]
           [Dashboard updates in real-time]

12:35:00 - Student turns HEAD RIGHT
12:35:08 - Duration: 3.0s - OFFENSE #2 LOGGED 🚨

12:40:00 - Student turns HEAD BACK
12:40:05 - Duration: 3.0s - OFFENSE #3 LOGGED 🚨
           [Student now has 3 offenses]
           [Dashboard shows: "🚨 FLAGGED" status]
           [Admin can now take action]
```

---

## 📱 Mobile Testing

The camera view is responsive and works on tablets/mobile:
```
Desktop (1920x1080):
│ Navbar                           │
│ Camera + Detection Info (2 cols) │
└──────────────────────────────────┘

Mobile (540px):
│ Navbar (icons only) │
│ Camera              │
│ Detection Info (1)  │
│ Pose Tracking       │
└────────────────────┘
```

---

## 🚀 Performance Tips

1. **For smooth detection:**
   - Close unnecessary applications
   - Ensure good CPU availability
   - Use well-lit environment

2. **For accuracy:**
   - Position camera 1-2 meters away
   - Ensure face is clearly visible
   - Avoid backlighting

3. **For real deployment:**
   - Use multiple camera angles
   - Implement server-side offenses storage
   - Add admin authentication
   - Enable persistent offense records

---

## ✅ Feature Checklist

- ✅ Admin can access Camera Monitor page
- ✅ Live webcam feed displays with detection overlays
- ✅ System detects head poses (forward/left/right/back)
- ✅ 3-second threshold triggers offense logging
- ✅ Real-time dashboard updates via WebSocket
- ✅ Flagged student list shows with offense counts
- ✅ Admin can reset/clear student offenses
- ✅ Color-coded visual indicators
- ✅ Responsive design works on mobile
- ✅ Mock mode works without vision packages

---

## 🎓 Learning Resources

After testing, explore:
1. **CAMERA_MONITORING_GUIDE.md** - Detailed system documentation
2. **API.md** - Backend API endpoints and WebSocket events
3. **ARCHITECTURE.md** - System design and data flow

---

**Questions?** Check the documentation or backend logs (terminal) for detailed error messages.

**Ready to test!** 🎯📹✨
