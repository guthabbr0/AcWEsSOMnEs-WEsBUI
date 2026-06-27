import { WEBUI_API_BASE_URL } from '$lib/constants';

const parseError = async (res: Response) => {
	const body = await res.json().catch(() => null);
	return body?.detail ?? body?.message ?? 'Request failed';
};

export const createModerationBan = async (token: string, ban: object) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/bans`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(ban)
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getModerationBans = async (
	token: string,
	userId: string | null = null,
	includeInactive = true
) => {
	let error = null;
	const params = new URLSearchParams();
	if (userId) params.set('user_id', userId);
	params.set('include_inactive', `${includeInactive}`);

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/bans?${params.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const revokeModerationBan = async (token: string, banId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/bans/${banId}/revoke`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getMyActiveModerationBans = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/me/active`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getModerationBanStatus = async (banId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/bans/${banId}/status`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const createModerationAppeal = async (banId: string, message: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/appeals`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			ban_id: banId,
			message
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getModerationAppeals = async (
	token: string,
	userId: string | null = null,
	statusFilter: string | null = null
) => {
	let error = null;
	const params = new URLSearchParams();
	if (userId) params.set('user_id', userId);
	if (statusFilter) params.set('status_filter', statusFilter);

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/appeals?${params.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const resolveModerationAppeal = async (
	token: string,
	appealId: string,
	status = 'resolved',
	resolutionNote = ''
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/appeals/${appealId}/resolve`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			status,
			resolution_note: resolutionNote
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getModerationAuditLogs = async (token: string, userId: string | null = null, limit = 100) => {
	let error = null;
	const params = new URLSearchParams();
	if (userId) params.set('user_id', userId);
	params.set('limit', `${limit}`);

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/audit?${params.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getModerationUserRisk = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/risk/${userId}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getModerationCenter = async (token: string, limit = 100) => {
	let error = null;
	const params = new URLSearchParams();
	params.set('limit', `${limit}`);

	const res = await fetch(`${WEBUI_API_BASE_URL}/moderation/center?${params.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await parseError(res);
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
