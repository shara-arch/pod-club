import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { createChannel, getChannel, getChannels, updateChannel } from './channelService';
import { getMessages, getThread, sendMessage, sendReply } from './messageService';

const getErrorMessage = (error) => error.message || 'Something went wrong. Please try again.';

export const loadChannels = createAsyncThunk('channels/loadChannels', getChannels);
export const loadChannel = createAsyncThunk('channels/loadChannel', getChannel);
export const addChannel = createAsyncThunk('channels/addChannel', createChannel);
export const saveChannel = createAsyncThunk(
  'channels/saveChannel',
  ({ channelId, values }) => updateChannel(channelId, values),
);
export const loadMessages = createAsyncThunk('channels/loadMessages', getMessages);
export const addMessage = createAsyncThunk(
  'channels/addMessage',
  ({ channelId, content }) => sendMessage(channelId, content),
);
export const loadThread = createAsyncThunk('channels/loadThread', getThread);
export const addReply = createAsyncThunk(
  'channels/addReply',
  ({ threadId, content }) => sendReply(threadId, content),
);

const initialState = {
  list: [],
  activeChannel: null,
  messagesByChannel: {},
  activeThread: null,
  status: 'idle',
  error: null,
};

const channelsSlice = createSlice({
  name: 'channels',
  initialState,
  reducers: {
    clearActiveChannel(state) {
      state.activeChannel = null;
    },
    clearActiveThread(state) {
      state.activeThread = null;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadChannels.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list = action.payload;
      })
      .addCase(loadChannel.pending, (state) => {
        state.activeChannel = null;
      })
      .addCase(loadChannel.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.activeChannel = action.payload;
      })
      .addCase(addChannel.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list.push(action.payload);
        state.activeChannel = action.payload;
      })
      .addCase(saveChannel.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.activeChannel = action.payload;
        const index = state.list.findIndex((channel) => channel.id === action.payload.id);
        if (index >= 0) state.list[index] = action.payload;
      })
      .addCase(loadMessages.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.messagesByChannel[action.meta.arg] = action.payload;
      })
      .addCase(addMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        const { channelId } = action.meta.arg;
        state.messagesByChannel[channelId] ||= [];
        state.messagesByChannel[channelId].push(action.payload);
      })
      .addCase(loadThread.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.activeThread = action.payload;
      })
      .addCase(addReply.fulfilled, (state, action) => {
        state.status = 'succeeded';
        if (state.activeThread?.id === action.meta.arg.threadId) {
          state.activeThread.replies.push(action.payload);
        }
      })
      .addMatcher((action) => action.type.endsWith('/pending'), (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addMatcher((action) => action.type.endsWith('/rejected'), (state, action) => {
        state.status = 'failed';
        state.error = getErrorMessage(action.error);
      });
  },
});

export const { clearActiveChannel, clearActiveThread, clearError } = channelsSlice.actions;
export default channelsSlice.reducer;
