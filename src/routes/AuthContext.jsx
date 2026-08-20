import React, {createContext, useContext, useState, useEffect} from 'react';

// Create a Context object to hold and share authentication state across components
const AuthContext = createContext(null);