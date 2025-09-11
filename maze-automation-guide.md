# Maze Game Automation Tools

## Overview
This directory contains various automation tools for the simple maze game using Selenium WebDriver and pathfinding algorithms.

## Files

### 1. simple-maze-game.html
- **Description**: The maze game itself
- **Features**: 
  - 20x20 grid maze
  - Yellow circle player
  - Green square goal
  - Procedurally generated mazes
  - Stage progression

### 2. open_maze_game.py
- **Description**: Simply opens the maze game in Chrome
- **Usage**: `python open_maze_game.py`
- **Features**: Keeps browser open after script ends

### 3. maze_auto_solver.py
- **Description**: Basic maze solver using BFS algorithm
- **Usage**: `python maze_auto_solver.py`
- **Features**:
  - Breadth-First Search pathfinding
  - Automatically solves 3 stages
  - Console output of progress

### 4. maze_solver_with_log.py
- **Description**: Enhanced solver with logging capabilities
- **Usage**: `python maze_solver_with_log.py`
- **Features**:
  - Detailed logging to text and JSON files
  - Timestamp for every event
  - Alert detection and logging
  - Performance metrics

### 5. maze_solver_visual.py
- **Description**: Visual path solver with on-screen path display
- **Usage**: `python maze_solver_visual.py`
- **Features**:
  - Draws the planned path in cyan before execution
  - Keeps browser open after completion
  - Visual feedback for debugging
  - Progress indicators

## How It Works

### Alert Detection
```python
try:
    alert = self.driver.switch_to.alert
    alert_text = alert.text
    alert.accept()
    return True
except:
    return False
```

### BFS Pathfinding
The solver uses Breadth-First Search to find the shortest path:
1. Start from player position
2. Explore all adjacent cells
3. Mark visited cells
4. Find path to goal
5. Return list of directions

### Logging System
- **Text logs**: Human-readable format with timestamps
- **JSON logs**: Machine-parsable format for analysis
- **Event types**: SYSTEM, GAME, SOLVER, ALERT, CLEAR, ERROR

## Log File Examples

### Text Log Format
```
[2025-01-20 14:30:15.123] [STAGE] ステージ 1 開始
[2025-01-20 14:30:15.234] [SOLVER] 経路発見: 32ステップ, 探索時間: 0.015秒
[2025-01-20 14:30:18.456] [ALERT] アラート検知: 'クリア！ ステップ数: 32'
[2025-01-20 14:30:18.567] [CLEAR] ステージ 1 クリア！
```

### JSON Log Format
```json
{
  "timestamp": "2025-01-20 14:30:18.456",
  "event_type": "ALERT",
  "message": "アラート検知: 'クリア！ ステップ数: 32'",
  "unix_time": 1737357018.456
}
```

## Technical Details

### Selenium Setup
```python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)  # Keep browser open
```

### JavaScript Injection
The visual solver injects JavaScript functions to draw paths:
```javascript
window.visualizePath = function(path) {
    // Draws cyan line showing the planned route
}
```

## Performance Metrics
- Path finding: ~0.01-0.03 seconds per stage
- Execution: ~0.05-0.1 seconds per move
- Total time per stage: 2-5 seconds depending on path length