<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { toast } from 'svelte-sonner';

	import { getAdminConfig, updateAdminConfig } from '$lib/apis/auths';

	import Switch from '$lib/components/common/Switch.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');
	const t = (key: string, params?: Record<string, unknown>) => {
		const translator = get(i18n) as
			| { t?: (k: string, p?: Record<string, unknown>) => string }
			| undefined;
		return translator?.t ? translator.t(key, params) : key;
	};

	type SSOConfig = Record<string, unknown> & {
		ENABLE_OAUTH_LOGIN: boolean;
		ENABLE_OAUTH_SIGNUP: boolean;
		OAUTH_MERGE_ACCOUNTS_BY_EMAIL: boolean;
		OAUTH_TIMEOUT: string;
		OAUTH_AUDIENCE: string;
		GOOGLE_OAUTH_ENABLED: boolean;
		GOOGLE_CLIENT_ID: string;
		GOOGLE_CLIENT_SECRET: string;
		GOOGLE_OAUTH_SCOPE: string;
		GOOGLE_SERVER_METADATA_URL: string;
		GOOGLE_REDIRECT_URI: string;
		MICROSOFT_OAUTH_ENABLED: boolean;
		MICROSOFT_CLIENT_ID: string;
		MICROSOFT_CLIENT_SECRET: string;
		MICROSOFT_CLIENT_TENANT_ID: string;
		MICROSOFT_CLIENT_LOGIN_BASE_URL: string;
		MICROSOFT_CLIENT_PICTURE_URL: string;
		MICROSOFT_OAUTH_SCOPE: string;
		MICROSOFT_REDIRECT_URI: string;
		GITHUB_OAUTH_ENABLED: boolean;
		GITHUB_CLIENT_ID: string;
		GITHUB_CLIENT_SECRET: string;
		GITHUB_CLIENT_SCOPE: string;
		GITHUB_CLIENT_REDIRECT_URI: string;
		GITHUB_ACCESS_TOKEN_URL: string;
		GITHUB_AUTHORIZE_URL: string;
		GITHUB_API_BASE_URL: string;
		GITHUB_USERINFO_ENDPOINT: string;
		DISCORD_OAUTH_ENABLED: boolean;
		DISCORD_CLIENT_ID: string;
		DISCORD_CLIENT_SECRET: string;
		DISCORD_OAUTH_SCOPE: string;
		DISCORD_REDIRECT_URI: string;
		DISCORD_ACCESS_TOKEN_URL: string;
		DISCORD_AUTHORIZE_URL: string;
		DISCORD_API_BASE_URL: string;
		DISCORD_USERINFO_ENDPOINT: string;
		OIDC_OAUTH_ENABLED: boolean;
		OAUTH_PROVIDER_NAME: string;
		OAUTH_CLIENT_ID: string;
		OAUTH_CLIENT_SECRET: string;
		OPENID_PROVIDER_URL: string;
		OPENID_REDIRECT_URI: string;
		OAUTH_SCOPES: string;
		OAUTH_TOKEN_ENDPOINT_AUTH_METHOD: string;
		OAUTH_CODE_CHALLENGE_METHOD: string;
		OAUTH_SUB_CLAIM: string;
		OAUTH_USERNAME_CLAIM: string;
		OAUTH_EMAIL_CLAIM: string;
		OAUTH_PICTURE_CLAIM: string;
		OAUTH_GROUPS_CLAIM: string;
		FEISHU_OAUTH_ENABLED: boolean;
		FEISHU_CLIENT_ID: string;
		FEISHU_CLIENT_SECRET: string;
		FEISHU_OAUTH_SCOPE: string;
		FEISHU_REDIRECT_URI: string;
		FEISHU_ACCESS_TOKEN_URL: string;
		FEISHU_AUTHORIZE_URL: string;
		FEISHU_API_BASE_URL: string;
		FEISHU_USERINFO_ENDPOINT: string;
		GITLAB_OAUTH_ENABLED: boolean;
		GITLAB_CLIENT_ID: string;
		GITLAB_CLIENT_SECRET: string;
		GITLAB_OAUTH_SCOPE: string;
		GITLAB_REDIRECT_URI: string;
		GITLAB_ACCESS_TOKEN_URL: string;
		GITLAB_AUTHORIZE_URL: string;
		GITLAB_API_BASE_URL: string;
		GITLAB_USERINFO_ENDPOINT: string;
		SLACK_OAUTH_ENABLED: boolean;
		SLACK_CLIENT_ID: string;
		SLACK_CLIENT_SECRET: string;
		SLACK_OAUTH_SCOPE: string;
		SLACK_REDIRECT_URI: string;
		SLACK_ACCESS_TOKEN_URL: string;
		SLACK_AUTHORIZE_URL: string;
		SLACK_API_BASE_URL: string;
		SLACK_USERINFO_ENDPOINT: string;
	};

	let adminConfig: SSOConfig | null = null;
	let providerCards: {
		id: string;
		enabledKey: keyof SSOConfig;
		label: string;
		abbr: string;
		enabled: boolean;
		configured: boolean;
	}[] = [];
	let enabledProviderCount = 0;
	let configuredProviderCount = 0;

	const normalizeConfig = (configData: Record<string, unknown>): SSOConfig => ({
		...configData,
		ENABLE_OAUTH_LOGIN: Boolean(configData?.ENABLE_OAUTH_LOGIN ?? true),
		ENABLE_OAUTH_SIGNUP: Boolean(configData?.ENABLE_OAUTH_SIGNUP ?? false),
		OAUTH_MERGE_ACCOUNTS_BY_EMAIL: Boolean(configData?.OAUTH_MERGE_ACCOUNTS_BY_EMAIL ?? false),
		OAUTH_TIMEOUT: String(configData?.OAUTH_TIMEOUT ?? ''),
		OAUTH_AUDIENCE: String(configData?.OAUTH_AUDIENCE ?? ''),
		GOOGLE_OAUTH_ENABLED: Boolean(configData?.GOOGLE_OAUTH_ENABLED ?? true),
		GOOGLE_CLIENT_ID: String(configData?.GOOGLE_CLIENT_ID ?? ''),
		GOOGLE_CLIENT_SECRET: String(configData?.GOOGLE_CLIENT_SECRET ?? ''),
		GOOGLE_OAUTH_SCOPE: String(configData?.GOOGLE_OAUTH_SCOPE ?? 'openid email profile'),
		GOOGLE_SERVER_METADATA_URL: String(
			configData?.GOOGLE_SERVER_METADATA_URL ??
				'https://accounts.google.com/.well-known/openid-configuration'
		),
		GOOGLE_REDIRECT_URI: String(configData?.GOOGLE_REDIRECT_URI ?? ''),
		MICROSOFT_OAUTH_ENABLED: Boolean(configData?.MICROSOFT_OAUTH_ENABLED ?? true),
		MICROSOFT_CLIENT_ID: String(configData?.MICROSOFT_CLIENT_ID ?? ''),
		MICROSOFT_CLIENT_SECRET: String(configData?.MICROSOFT_CLIENT_SECRET ?? ''),
		MICROSOFT_CLIENT_TENANT_ID: String(configData?.MICROSOFT_CLIENT_TENANT_ID ?? ''),
		MICROSOFT_CLIENT_LOGIN_BASE_URL: String(
			configData?.MICROSOFT_CLIENT_LOGIN_BASE_URL ?? 'https://login.microsoftonline.com'
		),
		MICROSOFT_CLIENT_PICTURE_URL: String(
			configData?.MICROSOFT_CLIENT_PICTURE_URL ?? 'https://graph.microsoft.com/v1.0/me/photo/$value'
		),
		MICROSOFT_OAUTH_SCOPE: String(configData?.MICROSOFT_OAUTH_SCOPE ?? 'openid email profile'),
		MICROSOFT_REDIRECT_URI: String(configData?.MICROSOFT_REDIRECT_URI ?? ''),
		GITHUB_OAUTH_ENABLED: Boolean(configData?.GITHUB_OAUTH_ENABLED ?? true),
		GITHUB_CLIENT_ID: String(configData?.GITHUB_CLIENT_ID ?? ''),
		GITHUB_CLIENT_SECRET: String(configData?.GITHUB_CLIENT_SECRET ?? ''),
		GITHUB_CLIENT_SCOPE: String(configData?.GITHUB_CLIENT_SCOPE ?? 'user:email'),
		GITHUB_CLIENT_REDIRECT_URI: String(configData?.GITHUB_CLIENT_REDIRECT_URI ?? ''),
		GITHUB_ACCESS_TOKEN_URL: String(
			configData?.GITHUB_ACCESS_TOKEN_URL ?? 'https://github.com/login/oauth/access_token'
		),
		GITHUB_AUTHORIZE_URL: String(
			configData?.GITHUB_AUTHORIZE_URL ?? 'https://github.com/login/oauth/authorize'
		),
		GITHUB_API_BASE_URL: String(configData?.GITHUB_API_BASE_URL ?? 'https://api.github.com'),
		GITHUB_USERINFO_ENDPOINT: String(
			configData?.GITHUB_USERINFO_ENDPOINT ?? 'https://api.github.com/user'
		),
		DISCORD_OAUTH_ENABLED: Boolean(configData?.DISCORD_OAUTH_ENABLED ?? true),
		DISCORD_CLIENT_ID: String(configData?.DISCORD_CLIENT_ID ?? ''),
		DISCORD_CLIENT_SECRET: String(configData?.DISCORD_CLIENT_SECRET ?? ''),
		DISCORD_OAUTH_SCOPE: String(configData?.DISCORD_OAUTH_SCOPE ?? 'identify email'),
		DISCORD_REDIRECT_URI: String(configData?.DISCORD_REDIRECT_URI ?? ''),
		DISCORD_ACCESS_TOKEN_URL: String(
			configData?.DISCORD_ACCESS_TOKEN_URL ?? 'https://discord.com/api/oauth2/token'
		),
		DISCORD_AUTHORIZE_URL: String(
			configData?.DISCORD_AUTHORIZE_URL ?? 'https://discord.com/oauth2/authorize'
		),
		DISCORD_API_BASE_URL: String(configData?.DISCORD_API_BASE_URL ?? 'https://discord.com/api'),
		DISCORD_USERINFO_ENDPOINT: String(
			configData?.DISCORD_USERINFO_ENDPOINT ?? 'https://discord.com/api/users/@me'
		),
		OIDC_OAUTH_ENABLED: Boolean(configData?.OIDC_OAUTH_ENABLED ?? true),
		OAUTH_PROVIDER_NAME: String(configData?.OAUTH_PROVIDER_NAME ?? 'SSO'),
		OAUTH_CLIENT_ID: String(configData?.OAUTH_CLIENT_ID ?? ''),
		OAUTH_CLIENT_SECRET: String(configData?.OAUTH_CLIENT_SECRET ?? ''),
		OPENID_PROVIDER_URL: String(configData?.OPENID_PROVIDER_URL ?? ''),
		OPENID_REDIRECT_URI: String(configData?.OPENID_REDIRECT_URI ?? ''),
		OAUTH_SCOPES: String(configData?.OAUTH_SCOPES ?? 'openid email profile'),
		OAUTH_TOKEN_ENDPOINT_AUTH_METHOD: String(configData?.OAUTH_TOKEN_ENDPOINT_AUTH_METHOD ?? ''),
		OAUTH_CODE_CHALLENGE_METHOD: String(configData?.OAUTH_CODE_CHALLENGE_METHOD ?? ''),
		OAUTH_SUB_CLAIM: String(configData?.OAUTH_SUB_CLAIM ?? ''),
		OAUTH_USERNAME_CLAIM: String(configData?.OAUTH_USERNAME_CLAIM ?? 'name'),
		OAUTH_EMAIL_CLAIM: String(configData?.OAUTH_EMAIL_CLAIM ?? 'email'),
		OAUTH_PICTURE_CLAIM: String(configData?.OAUTH_PICTURE_CLAIM ?? 'picture'),
		OAUTH_GROUPS_CLAIM: String(configData?.OAUTH_GROUPS_CLAIM ?? 'groups'),
		FEISHU_OAUTH_ENABLED: Boolean(configData?.FEISHU_OAUTH_ENABLED ?? true),
		FEISHU_CLIENT_ID: String(configData?.FEISHU_CLIENT_ID ?? ''),
		FEISHU_CLIENT_SECRET: String(configData?.FEISHU_CLIENT_SECRET ?? ''),
		FEISHU_OAUTH_SCOPE: String(configData?.FEISHU_OAUTH_SCOPE ?? 'contact:user.base:readonly'),
		FEISHU_REDIRECT_URI: String(configData?.FEISHU_REDIRECT_URI ?? ''),
		FEISHU_ACCESS_TOKEN_URL: String(
			configData?.FEISHU_ACCESS_TOKEN_URL ??
				'https://open.feishu.cn/open-apis/authen/v2/oauth/token'
		),
		FEISHU_AUTHORIZE_URL: String(
			configData?.FEISHU_AUTHORIZE_URL ?? 'https://accounts.feishu.cn/open-apis/authen/v1/authorize'
		),
		FEISHU_API_BASE_URL: String(
			configData?.FEISHU_API_BASE_URL ?? 'https://open.feishu.cn/open-apis'
		),
		FEISHU_USERINFO_ENDPOINT: String(
			configData?.FEISHU_USERINFO_ENDPOINT ?? 'https://open.feishu.cn/open-apis/authen/v1/user_info'
		),
		GITLAB_OAUTH_ENABLED: Boolean(configData?.GITLAB_OAUTH_ENABLED ?? true),
		GITLAB_CLIENT_ID: String(configData?.GITLAB_CLIENT_ID ?? ''),
		GITLAB_CLIENT_SECRET: String(configData?.GITLAB_CLIENT_SECRET ?? ''),
		GITLAB_OAUTH_SCOPE: String(configData?.GITLAB_OAUTH_SCOPE ?? 'openid profile email'),
		GITLAB_REDIRECT_URI: String(configData?.GITLAB_REDIRECT_URI ?? ''),
		GITLAB_ACCESS_TOKEN_URL: String(
			configData?.GITLAB_ACCESS_TOKEN_URL ?? 'https://gitlab.com/oauth/token'
		),
		GITLAB_AUTHORIZE_URL: String(
			configData?.GITLAB_AUTHORIZE_URL ?? 'https://gitlab.com/oauth/authorize'
		),
		GITLAB_API_BASE_URL: String(configData?.GITLAB_API_BASE_URL ?? 'https://gitlab.com/api/v4'),
		GITLAB_USERINFO_ENDPOINT: String(
			configData?.GITLAB_USERINFO_ENDPOINT ?? 'https://gitlab.com/oauth/userinfo'
		),
		SLACK_OAUTH_ENABLED: Boolean(configData?.SLACK_OAUTH_ENABLED ?? true),
		SLACK_CLIENT_ID: String(configData?.SLACK_CLIENT_ID ?? ''),
		SLACK_CLIENT_SECRET: String(configData?.SLACK_CLIENT_SECRET ?? ''),
		SLACK_OAUTH_SCOPE: String(configData?.SLACK_OAUTH_SCOPE ?? 'openid profile email'),
		SLACK_REDIRECT_URI: String(configData?.SLACK_REDIRECT_URI ?? ''),
		SLACK_ACCESS_TOKEN_URL: String(
			configData?.SLACK_ACCESS_TOKEN_URL ?? 'https://slack.com/api/openid.connect.token'
		),
		SLACK_AUTHORIZE_URL: String(
			configData?.SLACK_AUTHORIZE_URL ?? 'https://slack.com/openid/connect/authorize'
		),
		SLACK_API_BASE_URL: String(configData?.SLACK_API_BASE_URL ?? 'https://slack.com/api'),
		SLACK_USERINFO_ENDPOINT: String(
			configData?.SLACK_USERINFO_ENDPOINT ?? 'https://slack.com/api/openid.connect.userInfo'
		)
	});

	$: providerCards = adminConfig
		? [
				{
					id: 'google',
					enabledKey: 'GOOGLE_OAUTH_ENABLED',
					label: 'Google',
					abbr: 'G',
					enabled: adminConfig.GOOGLE_OAUTH_ENABLED,
					configured: Boolean(adminConfig.GOOGLE_CLIENT_ID && adminConfig.GOOGLE_CLIENT_SECRET)
				},
				{
					id: 'microsoft',
					enabledKey: 'MICROSOFT_OAUTH_ENABLED',
					label: 'Microsoft',
					abbr: 'MS',
					enabled: adminConfig.MICROSOFT_OAUTH_ENABLED,
					configured: Boolean(
						adminConfig.MICROSOFT_CLIENT_ID &&
						adminConfig.MICROSOFT_CLIENT_SECRET &&
						adminConfig.MICROSOFT_CLIENT_TENANT_ID
					)
				},
				{
					id: 'github',
					enabledKey: 'GITHUB_OAUTH_ENABLED',
					label: 'GitHub',
					abbr: 'GH',
					enabled: adminConfig.GITHUB_OAUTH_ENABLED,
					configured: Boolean(adminConfig.GITHUB_CLIENT_ID && adminConfig.GITHUB_CLIENT_SECRET)
				},
				{
					id: 'discord',
					enabledKey: 'DISCORD_OAUTH_ENABLED',
					label: 'Discord',
					abbr: 'DC',
					enabled: adminConfig.DISCORD_OAUTH_ENABLED,
					configured: Boolean(adminConfig.DISCORD_CLIENT_ID && adminConfig.DISCORD_CLIENT_SECRET)
				},
				{
					id: 'gitlab',
					enabledKey: 'GITLAB_OAUTH_ENABLED',
					label: 'GitLab',
					abbr: 'GL',
					enabled: adminConfig.GITLAB_OAUTH_ENABLED,
					configured: Boolean(adminConfig.GITLAB_CLIENT_ID && adminConfig.GITLAB_CLIENT_SECRET)
				},
				{
					id: 'slack',
					enabledKey: 'SLACK_OAUTH_ENABLED',
					label: 'Slack',
					abbr: 'SL',
					enabled: adminConfig.SLACK_OAUTH_ENABLED,
					configured: Boolean(adminConfig.SLACK_CLIENT_ID && adminConfig.SLACK_CLIENT_SECRET)
				},
				{
					id: 'feishu',
					enabledKey: 'FEISHU_OAUTH_ENABLED',
					label: 'Feishu',
					abbr: 'FS',
					enabled: adminConfig.FEISHU_OAUTH_ENABLED,
					configured: Boolean(adminConfig.FEISHU_CLIENT_ID && adminConfig.FEISHU_CLIENT_SECRET)
				},
				{
					id: 'oidc',
					enabledKey: 'OIDC_OAUTH_ENABLED',
					label: 'OIDC',
					abbr: 'ID',
					enabled: adminConfig.OIDC_OAUTH_ENABLED,
					configured: Boolean(adminConfig.OAUTH_CLIENT_ID && adminConfig.OPENID_PROVIDER_URL)
				}
			].sort(
				(a, b) =>
					Number(b.enabled) - Number(a.enabled) ||
					Number(b.configured) - Number(a.configured) ||
					a.label.localeCompare(b.label)
			)
		: [];

	$: enabledProviderCount = providerCards.filter((provider) => provider.enabled).length;
	$: configuredProviderCount = providerCards.filter((provider) => provider.configured).length;

	const providerConfigs = {
		google: {
			label: 'Google',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="size-4" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>`,
			fields: [
				{ key: 'GOOGLE_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'GOOGLE_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'GOOGLE_OAUTH_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'GOOGLE_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'GOOGLE_SERVER_METADATA_URL', placeholder: 'Server metadata URL', type: 'text', span: 2 }
			]
		},
		gitlab: {
			label: 'GitLab',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4" aria-hidden="true"><path fill="#E24329" d="m22.5 9.5-2.1-6.5a.8.8 0 0 0-.76-.54H4.36a.8.8 0 0 0-.76.54L1.5 9.5a1.43 1.43 0 0 0 .52 1.6l9.47 7.02 9.47-7.02a1.43 1.43 0 0 0 .52-1.6Z"/><path fill="#FC6D26" d="M12 18.2 15.5 7.4h-7L12 18.2Z" /><path fill="#FCA326" d="M8.5 7.4 6.9 2.5H4.3l4.2 4.9Z" /></svg>`,
			fields: [
				{ key: 'GITLAB_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'GITLAB_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'GITLAB_OAUTH_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'GITLAB_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'GITLAB_AUTHORIZE_URL', placeholder: 'Authorize URL', type: 'text' },
				{ key: 'GITLAB_ACCESS_TOKEN_URL', placeholder: 'Access token URL', type: 'text' },
				{ key: 'GITLAB_API_BASE_URL', placeholder: 'API base URL', type: 'text' },
				{ key: 'GITLAB_USERINFO_ENDPOINT', placeholder: 'Userinfo endpoint', type: 'text' }
			]
		},
		slack: {
			label: 'Slack',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4" aria-hidden="true"><path fill="#4A154B" d="M6.3 15.2a2 2 0 1 1-2 2h2v-2Zm1 0h3v2a2 2 0 1 1-2-2h-1v-0Zm1-8a2 2 0 1 1 2 2h-2v-2Zm0 1h2.9v3H8.3a2 2 0 1 1 0-3Zm8 1a2 2 0 1 1 2-2v2h-2Zm-1 0V6.3h2v2.9a2 2 0 1 1-2 0Zm1 8a2 2 0 1 1-2-2h2v2Zm-1-1h-2.9v-3h2.9a2 2 0 1 1 0 3Z"/></svg>`,
			fields: [
				{ key: 'SLACK_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'SLACK_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'SLACK_OAUTH_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'SLACK_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'SLACK_AUTHORIZE_URL', placeholder: 'Authorize URL', type: 'text' },
				{ key: 'SLACK_ACCESS_TOKEN_URL', placeholder: 'Access token URL', type: 'text' },
				{ key: 'SLACK_API_BASE_URL', placeholder: 'API base URL', type: 'text' },
				{ key: 'SLACK_USERINFO_ENDPOINT', placeholder: 'Userinfo endpoint', type: 'text' }
			]
		},
		microsoft: {
			label: 'Microsoft',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 21 21" class="size-4" aria-hidden="true"><rect x="1" y="1" width="9" height="9" fill="#f25022" /><rect x="1" y="11" width="9" height="9" fill="#00a4ef" /><rect x="11" y="1" width="9" height="9" fill="#7fba00" /><rect x="11" y="11" width="9" height="9" fill="#ffb900" /></svg>`,
			fields: [
				{ key: 'MICROSOFT_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'MICROSOFT_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'MICROSOFT_CLIENT_TENANT_ID', placeholder: 'Tenant ID', type: 'text' },
				{ key: 'MICROSOFT_OAUTH_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'MICROSOFT_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'MICROSOFT_CLIENT_LOGIN_BASE_URL', placeholder: 'Login base URL', type: 'text' },
				{ key: 'MICROSOFT_CLIENT_PICTURE_URL', placeholder: 'Picture URL', type: 'text', span: 2 }
			]
		},
		github: {
			label: 'GitHub',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M12.006 2a9.847 9.847 0 0 0-6.484 2.44 10.32 10.32 0 0 0-3.393 6.17 10.48 10.48 0 0 0 1.317 6.955 10.045 10.045 0 0 0 5.4 4.418c.504.095.683-.223.683-.494 0-.245-.01-1.052-.014-1.908-2.78.62-3.366-1.21-3.366-1.21a2.711 2.711 0 0 0-1.11-1.5c-.907-.637.07-.621.07-.621.317.044.62.163.885.346.266.183.487.426.647.71.135.253.318.476.538.655a2.079 2.079 0 0 0 2.37.196c.045-.52.27-1.006.635-1.37-2.219-.259-4.554-1.138-4.554-5.07a4.022 4.022 0 0 1 1.031-2.75 3.77 3.77 0 0 1 .096-2.713s.839-.275 2.749 1.05a9.26 9.26 0 0 1 5.004 0c1.906-1.325 2.74-1.05 2.74-1.05.37.858.406 1.828.101 2.713a4.017 4.017 0 0 1 1.029 2.75c0 3.939-2.339 4.805-4.564 5.058a2.471 2.471 0 0 1 .679 1.897c0 1.372-.012 2.477-.012 2.814 0 .272.18.592.687.492a10.05 10.05 0 0 0 5.388-4.421 10.473 10.473 0 0 0 1.313-6.948 10.32 10.32 0 0 0-3.39-6.165A9.847 9.847 0 0 0 12.007 2Z" clip-rule="evenodd" /></svg>`,
			fields: [
				{ key: 'GITHUB_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'GITHUB_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'GITHUB_CLIENT_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'GITHUB_CLIENT_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'GITHUB_AUTHORIZE_URL', placeholder: 'Authorize URL', type: 'text' },
				{ key: 'GITHUB_ACCESS_TOKEN_URL', placeholder: 'Access token URL', type: 'text' },
				{ key: 'GITHUB_API_BASE_URL', placeholder: 'API base URL', type: 'text' },
				{ key: 'GITHUB_USERINFO_ENDPOINT', placeholder: 'Userinfo endpoint', type: 'text' }
			]
		},
		discord: {
			label: 'Discord',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 199" class="size-4" aria-hidden="true"><path fill="currentColor" d="M216.9 16.6A208.5 208.5 0 0 0 163.3 0a150.5 150.5 0 0 0-6.8 13.9a193.2 193.2 0 0 0-57 0A150.5 150.5 0 0 0 92.7 0A208.5 208.5 0 0 0 39.1 16.6C5.2 67.5-3.9 117.1.6 165.8a209.9 209.9 0 0 0 64.7 33.2a161.8 161.8 0 0 0 13.9-22.6a133.7 133.7 0 0 1-21.9-10.5c1.9-1.4 3.7-2.8 5.4-4.3c42.3 19.8 88.2 19.8 130 0c1.8 1.5 3.6 2.9 5.4 4.3a133.7 133.7 0 0 1-21.9 10.5a161.8 161.8 0 0 0 13.9 22.6a209.9 209.9 0 0 0 64.7-33.2c5.3-56.4-9.1-105.5-37.9-149.2ZM85.5 135.6c-12.6 0-22.9-11.6-22.9-25.8s10.1-25.8 22.9-25.8s23.1 11.6 22.9 25.8s-10.2 25.8-22.9 25.8Zm84.9 0c-12.6 0-22.9-11.6-22.9-25.8s10.1-25.8 22.9-25.8s23.1 11.6 22.9 25.8s-10.2 25.8-22.9 25.8Z"/></svg>`,
			fields: [
				{ key: 'DISCORD_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'DISCORD_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'DISCORD_OAUTH_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'DISCORD_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'DISCORD_AUTHORIZE_URL', placeholder: 'Authorize URL', type: 'text' },
				{ key: 'DISCORD_ACCESS_TOKEN_URL', placeholder: 'Access token URL', type: 'text' },
				{ key: 'DISCORD_API_BASE_URL', placeholder: 'API base URL', type: 'text' },
				{ key: 'DISCORD_USERINFO_ENDPOINT', placeholder: 'Userinfo endpoint', type: 'text' }
			]
		},
		oidc: {
			label: 'OIDC',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z" /></svg>`,
			fields: [
				{ key: 'OAUTH_PROVIDER_NAME', placeholder: 'Provider name', type: 'text' },
				{ key: 'OAUTH_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'OAUTH_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'OPENID_PROVIDER_URL', placeholder: 'Provider URL', type: 'text' },
				{ key: 'OPENID_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'OAUTH_SCOPES', placeholder: 'Scopes', type: 'text' },
				{ key: 'OAUTH_TOKEN_ENDPOINT_AUTH_METHOD', placeholder: 'Token endpoint auth method', type: 'text' },
				{ key: 'OAUTH_CODE_CHALLENGE_METHOD', placeholder: 'Code challenge method', type: 'select', options: ['', 'S256'] },
				{ key: 'OAUTH_SUB_CLAIM', placeholder: 'Sub claim', type: 'text' },
				{ key: 'OAUTH_USERNAME_CLAIM', placeholder: 'Username claim', type: 'text' },
				{ key: 'OAUTH_EMAIL_CLAIM', placeholder: 'Email claim', type: 'text' },
				{ key: 'OAUTH_PICTURE_CLAIM', placeholder: 'Picture claim', type: 'text' },
				{ key: 'OAUTH_GROUPS_CLAIM', placeholder: 'Groups claim', type: 'text' }
			]
		},
		feishu: {
			label: 'Feishu',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-4" aria-hidden="true"><rect x="3" y="3" width="8" height="8" rx="2" fill="#00C4CC" /><rect x="13" y="3" width="8" height="8" rx="2" fill="#3370FF" /><rect x="3" y="13" width="8" height="8" rx="2" fill="#14C180" /><rect x="13" y="13" width="8" height="8" rx="2" fill="#FF8A00" /></svg>`,
			fields: [
				{ key: 'FEISHU_CLIENT_ID', placeholder: 'Client ID', type: 'text' },
				{ key: 'FEISHU_CLIENT_SECRET', placeholder: 'Client Secret', type: 'password' },
				{ key: 'FEISHU_OAUTH_SCOPE', placeholder: 'Scopes', type: 'text' },
				{ key: 'FEISHU_REDIRECT_URI', placeholder: 'Redirect URI', type: 'text' },
				{ key: 'FEISHU_AUTHORIZE_URL', placeholder: 'Authorize URL', type: 'text' },
				{ key: 'FEISHU_ACCESS_TOKEN_URL', placeholder: 'Access token URL', type: 'text' },
				{ key: 'FEISHU_API_BASE_URL', placeholder: 'API base URL', type: 'text' },
				{ key: 'FEISHU_USERINFO_ENDPOINT', placeholder: 'Userinfo endpoint', type: 'text' }
			]
		}
	};

	const saveHandler = async () => {
		if (!adminConfig) {
			return;
		}

		const response = await updateAdminConfig(localStorage.token, adminConfig).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (response) {
			adminConfig = normalizeConfig(response);
			toast.success(t('SSO management settings updated'));
		}
	};

	const updateConfigValue = (key: keyof SSOConfig, value: unknown) => {
		if (!adminConfig) {
			return;
		}

		adminConfig = {
			...adminConfig,
			[key]: value
		};
	};

	onMount(async () => {
		const configResponse = await getAdminConfig(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (configResponse) {
			adminConfig = normalizeConfig(configResponse);
		}
	});
</script>

<form
	class="flex h-full flex-col justify-between text-sm"
	on:submit|preventDefault={saveHandler}
	autocomplete="off"
>
	<div class="h-full space-y-3 overflow-y-scroll scrollbar-hidden pr-1">
		{#if adminConfig}
			<section class="rounded-xl border border-gray-100 dark:border-gray-850 p-3 space-y-3">
				<div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
					<div>
						<div class="text-base font-medium">{$i18n.t('SSO Management')}</div>
						<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
							{$i18n.t('Configure OAuth providers. Enabled and configured providers stay at the top.')}
						</div>
					</div>
					<div class="flex shrink-0 gap-2 text-xs text-gray-500 dark:text-gray-400">
						<span class="rounded-lg bg-gray-50 px-2 py-1 dark:bg-gray-850">
							{enabledProviderCount}/{providerCards.length} {$i18n.t('enabled')}
						</span>
						<span class="rounded-lg bg-gray-50 px-2 py-1 dark:bg-gray-850">
							{configuredProviderCount}/{providerCards.length} {$i18n.t('configured')}
						</span>
					</div>
				</div>

				<div class="grid gap-2 md:grid-cols-2">
					<label class="flex items-center justify-between gap-3 rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-850">
						<span>
							<span class="block text-sm font-medium">{$i18n.t('SSO Logins')}</span>
							<span class="block text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Allow users to sign in with enabled providers.')}</span>
						</span>
						<Switch bind:state={adminConfig.ENABLE_OAUTH_LOGIN} />
					</label>

					<label class="flex items-center justify-between gap-3 rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-850">
						<span>
							<span class="block text-sm font-medium">{$i18n.t('SSO Registration')}</span>
							<span class="block text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Allow new accounts from enabled providers.')}</span>
						</span>
						<Switch bind:state={adminConfig.ENABLE_OAUTH_SIGNUP} />
					</label>
				</div>
			</section>

			<section class="space-y-2">
				{#each providerCards as provider (provider.id)}
					{@const config = providerConfigs[provider.id]}
					<details
						class="rounded-xl border border-gray-100 dark:border-gray-850 p-0 overflow-hidden bg-white/50 dark:bg-gray-900/30"
					>
						<summary class="list-none cursor-pointer px-3 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-850/60">
							<div class="flex items-center justify-between gap-3">
								<div class="flex min-w-0 items-center gap-2.5">
									<div class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gray-50 text-gray-700 dark:bg-gray-850 dark:text-gray-200">
										{@html config.icon}
									</div>
									<div class="min-w-0">
										<div class="truncate text-sm font-medium">{config.label}</div>
										<div class="mt-0.5 flex flex-wrap gap-1.5 text-[11px]">
											<span class="rounded-md px-1.5 py-0.5 {provider.enabled ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300' : 'bg-gray-50 text-gray-500 dark:bg-gray-850 dark:text-gray-400'}">
												{provider.enabled ? $i18n.t('Enabled') : $i18n.t('Disabled')}
											</span>
											<span class="rounded-md px-1.5 py-0.5 {provider.configured ? 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300' : 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300'}">
												{provider.configured ? $i18n.t('Configured') : $i18n.t('Missing keys')}
											</span>
										</div>
									</div>
								</div>

								<div class="flex shrink-0 items-center gap-3" on:click|stopPropagation>
									<Switch
										state={Boolean(adminConfig[provider.enabledKey])}
										on:change={(event) => updateConfigValue(provider.enabledKey, event.detail)}
									/>
								</div>
							</div>
						</summary>

						<div class="border-t border-gray-100 p-3 dark:border-gray-850">
							<div class="grid gap-2 sm:grid-cols-2">
								{#each config.fields as field}
									<div class={field.span === 2 ? 'sm:col-span-2' : ''}>
											<label
												for="{provider.id}-{field.key}"
												class="mb-1 block text-[11px] font-medium text-gray-500 dark:text-gray-400"
											>
												{field.placeholder}
											</label>

										{#if field.type === 'select'}
												<select
													id="{provider.id}-{field.key}"
													class="w-full rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850 dark:bg-gray-900"
												value={String(adminConfig[field.key] ?? '')}
												autocomplete="off"
												on:change={(event) => updateConfigValue(field.key, event.currentTarget.value)}
											>
												{#each field.options ?? [] as option}
													<option value={option}>{option || $i18n.t('None')}</option>
												{/each}
											</select>
										{:else}
												<input
													id="{provider.id}-{field.key}"
													type={field.type === 'password' ? 'password' : 'text'}
												value={String(adminConfig[field.key] ?? '')}
												class="w-full rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden placeholder:text-gray-300 focus:border-gray-300 dark:border-gray-850 dark:placeholder:text-gray-700 dark:focus:border-gray-700"
												placeholder={field.placeholder}
												autocomplete="new-password"
												spellcheck="false"
												autocapitalize="off"
												on:input={(event) => updateConfigValue(field.key, event.currentTarget.value)}
											/>
										{/if}
									</div>
								{/each}
							</div>
						</div>
					</details>
				{/each}
			</section>

			<section class="rounded-xl border border-gray-100 dark:border-gray-850 p-3 space-y-3">
				<div>
					<div class="text-sm font-medium">{$i18n.t('Advanced')}</div>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t('Only change these when your provider requires them.')}
					</div>
				</div>

				<div class="grid gap-2 md:grid-cols-3">
					<label class="flex items-center justify-between gap-3 rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-850 md:col-span-1">
						<span>
							<span class="block text-xs font-medium">{$i18n.t('Merge by Email')}</span>
							<span class="block text-[11px] text-gray-500 dark:text-gray-400">{$i18n.t('Link matching existing users.')}</span>
						</span>
						<Switch bind:state={adminConfig.OAUTH_MERGE_ACCOUNTS_BY_EMAIL} />
					</label>

					<div>
							<label for="oauth-timeout-input" class="mb-1 block text-[11px] font-medium text-gray-500 dark:text-gray-400">{$i18n.t('Timeout')}</label>
							<input
								id="oauth-timeout-input"
								type="text"
							bind:value={adminConfig.OAUTH_TIMEOUT}
							class="w-full rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850"
							placeholder="30"
							autocomplete="off"
						/>
					</div>

					<div>
							<label for="oauth-audience-input" class="mb-1 block text-[11px] font-medium text-gray-500 dark:text-gray-400">{$i18n.t('Audience')}</label>
							<input
								id="oauth-audience-input"
								type="text"
							bind:value={adminConfig.OAUTH_AUDIENCE}
							class="w-full rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850"
							placeholder={$i18n.t('Optional')}
							autocomplete="off"
						/>
					</div>
				</div>
			</section>
		{:else}
			<div class="flex h-full justify-center">
				<div class="my-auto">
					<Spinner className="size-6" />
				</div>
			</div>
		{/if}
	</div>

	<div class="flex justify-end pt-3 text-sm font-medium">
		<button
			class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			type="submit"
		>
			{$i18n.t('Save')}
		</button>
	</div>
</form>
