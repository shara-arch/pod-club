import { configureStore } from '@reduxjs/toolkit';
import channelsReducer from '../features/channels/channelsSlice';

export const store = configureStore({
  reducer: {
    channels: channelsReducer,
  },
});
