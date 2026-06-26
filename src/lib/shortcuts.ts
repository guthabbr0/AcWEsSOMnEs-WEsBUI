type ShortcutRegistry = {
	[key in Shortcut]?: {
		name: string;
		keys: string[];
		category: string;
		tooltip?: string;
		setting?: {
			id: string;
			value: any;
		};
	};
};

export enum Shortcut {
	//Chat
	NEW_CHAT = 'newChat',
	NEW_TEMPORARY_CHAT = 'newTemporaryChat',
	DELETE_CHAT = 'deleteChat',
	OPEN_MODEL_SELECTOR = 'openModelSelector',
	TOGGLE_DICTATION = 'toggleDictation',

	//Global
	SEARCH = 'search',
	OPEN_SETTINGS = 'openSettings',
	SHOW_SHORTCUTS = 'showShortcuts',
	TOGGLE_SIDEBAR = 'toggleSidebar',
	CLOSE_MODAL = 'closeModal',

	//Input
	FOCUS_INPUT = 'focusInput',
	ACCEPT_AUTOCOMPLETE = 'acceptAutocomplete',
	PREVENT_FILE_CREATION = 'preventFileCreation',
	NAVIGATE_PROMPT_HISTORY_UP = 'navigatePromptHistoryUp',
	ATTACH_FILE = 'attachFile',
	ADD_PROMPT = 'addPrompt',
	TALK_TO_MODEL = 'talkToModel',

	//Message
	GENERATE_MESSAGE_PAIR = 'generateMessagePair',
	REGENERATE_RESPONSE = 'regenerateResponse',
	COPY_LAST_CODE_BLOCK = 'copyLastCodeBlock',
	COPY_LAST_RESPONSE = 'copyLastResponse',
	STOP_GENERATING = 'stopGenerating',
	EDIT_CHANNEL_MESSAGE = 'editChannelMessage',
	DELETE_CHANNEL_MESSAGE = 'deleteChannelMessage',
	REPLY_CHANNEL_MESSAGE = 'replyChannelMessage',
	PIN_CHANNEL_MESSAGE = 'pinChannelMessage',
	REACT_CHANNEL_MESSAGE = 'reactChannelMessage',
	COPY_CHANNEL_MESSAGE = 'copyChannelMessage',

	//Voice
	TOGGLE_MUTE = 'toggleMute'
}

export const shortcuts: ShortcutRegistry = {
	//Chat
	[Shortcut.NEW_CHAT]: {
		name: 'New Chat',
		keys: ['mod', 'shift', 'O'],
		category: 'Chat'
	},
	[Shortcut.NEW_TEMPORARY_CHAT]: {
		name: 'New Temporary Chat',
		keys: ['mod', 'shift', `'`],
		category: 'Chat'
	},
	[Shortcut.DELETE_CHAT]: {
		name: 'Delete Chat',
		keys: ['mod', 'shift', 'Backspace', 'Delete'],
		category: 'Chat'
	},
	[Shortcut.OPEN_MODEL_SELECTOR]: {
		name: 'Open Model Selector',
		keys: ['mod', 'shift', 'M'],
		category: 'Chat'
	},
	[Shortcut.TOGGLE_DICTATION]: {
		name: 'Toggle Dictation',
		keys: ['mod', 'shift', 'L'],
		category: 'Chat'
	},

	//Global
	[Shortcut.SEARCH]: {
		name: 'Search',
		keys: ['mod', 'K'],
		category: 'Global'
	},
	[Shortcut.OPEN_SETTINGS]: {
		name: 'Open Settings',
		keys: ['mod', '.'],
		category: 'Global'
	},
	[Shortcut.SHOW_SHORTCUTS]: {
		name: 'Show Shortcuts',
		keys: ['mod', '/'],
		category: 'Global'
	},
	[Shortcut.TOGGLE_SIDEBAR]: {
		name: 'Toggle Sidebar',
		keys: ['mod', 'shift', 'S'],
		category: 'Global'
	},
	[Shortcut.CLOSE_MODAL]: {
		name: 'Close Modal',
		keys: ['Escape'],
		category: 'Global'
	},

	//Input
	[Shortcut.FOCUS_INPUT]: {
		name: 'Focus Chat Input',
		keys: ['shift', 'Escape'],
		category: 'Input'
	},
	[Shortcut.ACCEPT_AUTOCOMPLETE]: {
		name: 'Accept Autocomplete Generation\nJump to Prompt Variable',
		keys: ['Tab'],
		category: 'Input'
	},
	[Shortcut.PREVENT_FILE_CREATION]: {
		name: 'Prevent File Creation',
		keys: ['mod', 'shift', 'V'],
		category: 'Input',
		tooltip: 'Only active when "Paste Large Text as File" setting is toggled on.'
	},
	[Shortcut.ATTACH_FILE]: {
		name: 'Attach File From Knowledge',
		keys: ['#'],
		category: 'Input'
	},
	[Shortcut.ADD_PROMPT]: {
		name: 'Add Custom Prompt',
		keys: ['/'],
		category: 'Input'
	},
	[Shortcut.TALK_TO_MODEL]: {
		name: 'Talk to Model',
		keys: ['@'],
		category: 'Input'
	},

	//Message
	[Shortcut.GENERATE_MESSAGE_PAIR]: {
		name: 'Generate Message Pair',
		keys: ['mod', 'shift', 'Enter'],
		category: 'Message',
		tooltip: 'Only active when the chat input is in focus.'
	},
	[Shortcut.REGENERATE_RESPONSE]: {
		name: 'Regenerate Response',
		keys: ['mod', 'R'],
		category: 'Message'
	},
	[Shortcut.STOP_GENERATING]: {
		name: 'Stop Generating',
		keys: ['Escape'],
		category: 'Message',
		tooltip: 'Only active when the chat input is in focus and an LLM is generating a response.'
	},
	[Shortcut.NAVIGATE_PROMPT_HISTORY_UP]: {
		name: 'Edit Last Message',
		keys: ['ArrowUp'],
		category: 'Message',
		tooltip: 'Only can be triggered when the chat input is in focus.'
	},
	[Shortcut.COPY_LAST_RESPONSE]: {
		name: 'Copy Last Response',
		keys: ['mod', 'shift', 'C'],
		category: 'Message'
	},
	[Shortcut.COPY_LAST_CODE_BLOCK]: {
		name: 'Copy Last Code Block',
		keys: ['mod', 'shift', ';'],
		category: 'Message'
	},
	[Shortcut.EDIT_CHANNEL_MESSAGE]: {
		name: 'Edit Channel Message',
		keys: ['E'],
		category: 'Channel Message',
		tooltip: 'Only active when focused on a channel message.'
	},
	[Shortcut.DELETE_CHANNEL_MESSAGE]: {
		name: 'Delete Channel Message',
		keys: ['Backspace'],
		category: 'Channel Message',
		tooltip: 'Only active when focused on a channel message.'
	},
	[Shortcut.REPLY_CHANNEL_MESSAGE]: {
		name: 'Reply to Channel Message',
		keys: ['R'],
		category: 'Channel Message',
		tooltip: 'Only active when focused on a channel message.'
	},
	[Shortcut.PIN_CHANNEL_MESSAGE]: {
		name: 'Pin Channel Message',
		keys: ['P'],
		category: 'Channel Message',
		tooltip: 'Only active when focused on a channel message.'
	},
	[Shortcut.REACT_CHANNEL_MESSAGE]: {
		name: 'Add Reaction',
		keys: ['+'],
		category: 'Channel Message',
		tooltip: 'Only active when focused on a channel message.'
	},
	[Shortcut.COPY_CHANNEL_MESSAGE]: {
		name: 'Copy Channel Message Text',
		keys: ['mod', 'C'],
		category: 'Channel Message',
		tooltip: 'Only active when focused on a channel message.'
	},

	//Voice
	[Shortcut.TOGGLE_MUTE]: {
		name: 'Toggle Mute',
		keys: ['M'],
		category: 'Voice',
		tooltip: 'Only active during Voice Mode.'
	}
};
