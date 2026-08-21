import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { createChannel, deleteChannel, getChannel, getChannels, updateChannel } from './channelService';
import { getMessages, getThread, removeMessage, sendImageMessage, sendMessage, sendReply, updateMessage } from './messageService';

const getErrorMessage = (error) => error.message || 'Something went wrong. Please try again.';

export const loadChannels = createAsyncThunk('channels/loadChannels', getChannels);
export const loadChannel = createAsyncThunk('channels/loadChannel', getChannel);
export const addChannel = createAsyncThunk('channels/addChannel', createChannel);
export const saveChannel = createAsyncThunk(
  'channels/saveChannel',
  ({ channelId, values }) => updateChannel(channelId, values),
);
export const removeChannel = createAsyncThunk('channels/removeChannel', deleteChannel);
export const loadMessages = createAsyncThunk('channels/loadMessages', getMessages);
export const addMessage = createAsyncThunk(
  'channels/addMessage',
  ({ channelId, content }) => sendMessage(channelId, content),
);
export const addImageMessage = createAsyncThunk('channels/addImageMessage', ({ channelId, imageUrl, caption }) => sendImageMessage(channelId, imageUrl, caption));
export const editMessage = createAsyncThunk('channels/editMessage', ({ messageId, content }) => updateMessage(messageId, content));
export const deleteMessage = createAsyncThunk('channels/deleteMessage', removeMessage);
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
      .addCase(removeChannel.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list = state.list.filter((channel) => channel.id !== action.meta.arg);
        state.activeChannel = null;
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
      .addCase(addImageMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        const { channelId } = action.meta.arg;
        state.messagesByChannel[channelId] ||= [];
        state.messagesByChannel[channelId].push(action.payload);
      })
      .addCase(editMessage.fulfilled, (state, action) => {
        const message = action.payload;
        const messages = state.messagesByChannel[message.channelId] || [];
        const index = messages.findIndex((item) => item.id === message.id);
        if (index >= 0) messages[index] = message;
      })
      .addCase(deleteMessage.fulfilled, (state, action) => {
        for (const channelId of Object.keys(state.messagesByChannel)) {
          state.messagesByChannel[channelId] = state.messagesByChannel[channelId].filter((message) => message.id !== action.meta.arg);
        }
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
