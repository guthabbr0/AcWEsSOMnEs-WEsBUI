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
