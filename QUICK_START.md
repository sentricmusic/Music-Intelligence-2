# QUICK START GUIDE - Music Intelligence Platform

## 🚀 IMMEDIATE STARTUP (Copy-Paste Ready)

### 1. Start Backend (Terminal 1)
```powershell
cd "C:\Users\kaz.roche\Desktop\music-intelligence\backend"
python simple_working.py
```

### 2. Start Frontend (Terminal 2) 
```powershell
cd "C:\Users\kaz.roche\Desktop\music-intelligence"
npm start
```

### 3. If Port 3000 Busy
```powershell
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
npm start
```

---

## 🎯 TEST WORKFLOW

1. **Open**: http://localhost:3000
2. **Select**: Market = "US", Genre = "Pop"  
3. **Click**: "Discover Playlists"
4. **Choose**: Any playlist from results
5. **Click**: "Load Tracks" 
6. **Click**: "Get Writer Credits (Apple Music)"
7. **Verify**: IPI numbers appear with writer credits

---

## 🔑 KEY FILES

- **Server**: `backend/simple_working.py`
- **Frontend**: `src/App.js` 
- **Credentials**: `AuthKey_FH2F6F277R.p8`
- **Config**: `backend/.env`

---

## ✅ EXPECTED RESULTS

- Apple Music Success: 100%
- Writer Credits: ~90% 
- IPI Numbers: Artist + Writer IPIs displayed
- Processing: 10 tracks (fast mode)

---

**STATUS: READY TO TEST IPI EXTRACTION** 🎉