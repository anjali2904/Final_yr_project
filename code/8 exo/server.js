// server.js

const express = require('express');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const app = express();
const PORT = 3000;

// Sample in-memory database
const users = [];

// Middleware for parsing JSON body
app.use(bodyParser.json());

// Signup endpoint
app.post('/signup', async (req, res) => {
    const { name, email, password } = req.body;
    
    // Check if email already exists
    if (users.some(user => user.email === email)) {
        return res.status(400).send('Email already exists');
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Store user data
    users.push({ name, email, password: hashedPassword });
    
    res.status(201).send('User created successfully');
});

// Login endpoint
app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    
    // Find user by email
    const user = users.find(user => user.email === email);
    if (!user) {
        return res.status(404).send('User not found');
    }
    
    // Compare passwords
    if (await bcrypt.compare(password, user.password)) {
        res.status(200).send('Login successful');
    } else {
        res.status(401).send('Invalid password');
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
