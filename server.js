require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Connect to MongoDB container
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('MongoDB Connected via .env.local'))
  .catch(err => console.log(err));

// 1. UPDATED: Define Task Schema with new fields
const TaskSchema = new mongoose.Schema({
  title: { type: String, required: true },
  status: { type: String, default: 'Pending' },
  category: { type: String, default: 'University' },
  priority: { type: String, default: 'Medium' },
  dueDate: { type: Date }
});
const Task = mongoose.model('Task', TaskSchema);

// API Routes
app.get('/api/tasks', async (req, res) => {
  const tasks = await Task.find();
  res.json(tasks);
});

// 2. UPDATED: POST route to handle the new frontend data
app.post('/api/tasks', async (req, res) => {
  const newTask = new Task({ 
    title: req.body.title,
    category: req.body.category,
    priority: req.body.priority,
    dueDate: req.body.dueDate
  });
  await newTask.save();
  res.json(newTask);
});

app.put('/api/tasks/:id', async (req, res) => {
  try {
    const task = await Task.findById(req.params.id);
    task.status = task.status === 'Pending' ? 'Completed' : 'Pending';
    await task.save();
    res.json(task);
  } catch (err) {
    res.status(500).send('Error updating status');
  }
});

app.delete('/api/tasks/:id', async (req, res) => {
  try {
    await Task.findByIdAndDelete(req.params.id);
    res.json({ message: 'Task deleted successfully' });
  } catch (err) {
    res.status(500).send('Error deleting task');
  }
});

// Serve Frontend
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(3000, () => console.log('Server running on port 3000'));