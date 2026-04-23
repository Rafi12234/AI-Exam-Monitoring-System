# 📋 AI Exam Monitoring System - Documentation Index

## 📖 START HERE

If you're new to this project, read the documentation in this order:

### 1️⃣ **First Time Setup**
   → Read: **[QUICKSTART.md](QUICKSTART.md)**
   - Installation steps for Windows/Linux/Mac
   - How to run the application
   - Troubleshooting common issues

### 2️⃣ **Understand the System**
   → Read: **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - How components work together
   - Data flow and communication
   - Technology stack details

### 3️⃣ **Complete Reference**
   → Read: **[README.md](README.md)**
   - Full feature list
   - Project requirements
   - Detailed setup instructions

### 4️⃣ **API Integration**
   → Read: **[API.md](API.md)**
   - All REST endpoints
   - WebSocket events
   - Usage examples

### 5️⃣ **File Details**
   → Read: **[FILE_INVENTORY.md](FILE_INVENTORY.md)**
   - All 40+ files explained
   - File organization
   - Lines of code breakdown

### 6️⃣ **Project Summary**
   → Read: **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)**
   - What was created
   - Features included
   - Next steps

---

## 🎯 Quick Navigation

### 🚀 **I Want To Get Started NOW**
```bash
# Windows:
setup.bat
start.bat

# Linux/Mac:
chmod +x setup.sh start.sh
./setup.sh
./start.sh
```
→ Then visit: **http://localhost:3000**

---

### 📚 **I Want To Understand the Code**
1. Backend: `backend/app.py` (~400 lines)
2. Dashboard: `frontend/src/components/Dashboard.js` (~150 lines)
3. CV Pipeline: `backend/vision/cv_pipeline.py` (~100 lines)

---

### 🔗 **I Want To Use the APIs**
See: **[API.md](API.md)**

Examples:
```bash
# Get flagged students
curl http://localhost:5000/api/flagged_students

# Log an offense
curl -X POST http://localhost:5000/api/log_offense \
  -H "Content-Type: application/json" \
  -d '{"student_id":"STU_0001","behavior_type":"back"}'
```

---

### 🧠 **I Want To Train on CV Components**
Read these files in order:
1. `backend/vision/detector.py` - YOLO detection
2. `backend/vision/tracker.py` - DeepSORT tracking
3. `backend/vision/head_pose.py` - MediaPipe poses
4. `backend/vision/cv_pipeline.py` - Integration

---

### 🎨 **I Want To Customize the UI**
Files to modify:
- `frontend/src/components/Dashboard.css` - Main styles
- `frontend/src/components/FlaggedStudentCard.css` - Card styles
- `frontend/src/index.css` - Global styles

---

### 🗄️ **I Want To Understand the Database**
See database schema in: **[ARCHITECTURE.md](ARCHITECTURE.md#database-schema)**

Database file: `backend/database.db` (auto-created)

---

### 🧪 **I Want To Test Without CV Pipeline**
Run mock backend:
```bash
cd backend
python app_mock.py
```
Then start frontend normally

---

## 📂 File Organization

```
Root Directory:
├── 📖 QUICKSTART.md          ⭐ Start here!
├── 📖 README.md              Complete documentation
├── 📖 ARCHITECTURE.md         System design
├── 📖 API.md                 API reference
├── 📖 FILE_INVENTORY.md       All files explained
├── 📖 PROJECT_COMPLETE.md    Completion summary
├── 📖 INDEX.md               This file!
│
├── 📜 setup.bat / setup.sh   Installation scripts
├── 🚀 start.bat / start.sh   Startup scripts
├── ⚙️ .env.example            Environment template
│
├── 📁 backend/               Backend source code
│   ├── app.py               Main Flask app
│   ├── app_mock.py          Mock backend
│   └── vision/              Computer Vision
│
└── 📁 frontend/              Frontend source code
    └── src/
        ├── components/      React components
        ├── context/         State management
        └── utils/           Helpers & clients
```

---

## 🔑 Key Technologies

| Technology | Files | Purpose |
|-----------|-------|---------|
| **Flask** | `backend/app.py` | Backend API |
| **React** | `frontend/src/App.js` | Dashboard UI |
| **SQLite** | `backend/database.db` | Database |
| **YOLO** | `backend/vision/detector.py` | Detection |
| **DeepSORT** | `backend/vision/tracker.py` | Tracking |
| **MediaPipe** | `backend/vision/head_pose.py` | Pose estimation |
| **Socket.IO** | `frontend/src/utils/socket.js` | Real-time updates |
| **Axios** | `frontend/src/utils/api.js` | API calls |

---

## ⚡ Common Tasks

### Task: Run the application
```bash
# Windows:
setup.bat && start.bat

# Linux/Mac:
./setup.sh && ./start.sh
```

### Task: Test without CV pipeline
```bash
cd backend
python app_mock.py
```

### Task: Add new API endpoint
Edit: `backend/app.py`

### Task: Change dashboard styling
Edit: `frontend/src/components/Dashboard.css`

### Task: Adjust offense threshold
Edit: `backend/app.py` (line ~75: `if count >= 3`)

### Task: Change video source
Edit: `backend/vision/cv_pipeline.py` (line ~26: `video_source=0`)

### Task: Integrate with your API
See: **[API.md](API.md)** for all endpoints

---

## ❓ FAQ

**Q: How do I run just the frontend?**
```bash
cd frontend && npm start
```

**Q: How do I run just the backend?**
```bash
cd backend && python app.py
```

**Q: How do I run the CV pipeline?**
```bash
cd backend/vision && python cv_pipeline.py
```

**Q: Can I test without a camera?**
Yes! Use mock backend: `python backend/app_mock.py`

**Q: Where is the database?**
`backend/database.db` (auto-created on first run)

**Q: How do I connect to a specific camera?**
Edit `backend/vision/cv_pipeline.py` line 26

**Q: How do I change the offense threshold?**
Edit `backend/app.py` line ~75 (change `>= 3` to desired number)

**Q: Can I deploy this to production?**
Yes! See deployment section in **[README.md](README.md)**

---

## 📊 Project Statistics

- **Total Files**: 40+
- **Lines of Code**: 2000+
- **Python Files**: 10
- **React Files**: 15
- **CSS Files**: 6
- **Configuration Files**: 4
- **Documentation Files**: 6

---

## 🎓 Learning Resources

### For Backend Development
- Flask Tutorial: https://flask.palletsprojects.com/
- Flask-SocketIO: https://flask-socketio.readthedocs.io/
- SQLite: https://www.sqlite.org/

### For Frontend Development
- React Documentation: https://react.dev/
- Socket.IO Client: https://socket.io/docs/v4/client-api/
- Axios: https://axios-http.com/

### For Computer Vision
- YOLOv5: https://docs.ultralytics.com/
- DeepSORT: https://github.com/nwojke/deep_sort
- MediaPipe: https://mediapipe.dev/

---

## 📞 Support

### Issue: Backend won't connect
→ Check: `backend/app.py` is running on port 5000

### Issue: Frontend won't load
→ Check: `frontend/package.json` dependencies installed

### Issue: CV pipeline not working
→ Check: Camera permissions and backend connectivity

### Issue: Database error
→ Delete `backend/database.db` and restart (will recreate)

---

## 🚀 Deployment Checklist

Before going to production:
- [ ] Read README.md completely
- [ ] Test with mock data
- [ ] Set up HTTPS/SSL
- [ ] Configure authentication
- [ ] Set up logging
- [ ] Configure external database
- [ ] Set up monitoring
- [ ] Backup strategy
- [ ] Disaster recovery plan

---

## 📝 Document Navigation

| Document | Read Time | Best For |
|----------|-----------|----------|
| **QUICKSTART.md** | 10 min | Getting started |
| **README.md** | 20 min | Full understanding |
| **ARCHITECTURE.md** | 15 min | System design |
| **API.md** | 15 min | Integration |
| **FILE_INVENTORY.md** | 10 min | File reference |
| **PROJECT_COMPLETE.md** | 5 min | Summary |
| **INDEX.md** | 5 min | Navigation |

---

## 🎯 Quick Links

- **Setup Guide**: [QUICKSTART.md](QUICKSTART.md)
- **Full Docs**: [README.md](README.md)
- **System Design**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **APIs**: [API.md](API.md)
- **Files**: [FILE_INVENTORY.md](FILE_INVENTORY.md)

---

## ✅ You Now Have

✅ Complete frontend (React dashboard)
✅ Complete backend (Flask API)
✅ Computer vision pipeline (YOLO + DeepSORT + MediaPipe)
✅ Database (SQLite)
✅ Real-time communication (WebSocket)
✅ Comprehensive documentation
✅ Setup scripts
✅ Mock backend for testing

---

**🎉 You're ready to go! Start with [QUICKSTART.md](QUICKSTART.md)**

---

*Last Updated: April 23, 2026*
*Version: 1.0.0*
