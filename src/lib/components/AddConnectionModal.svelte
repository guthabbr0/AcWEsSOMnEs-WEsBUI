<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext, onMount } from 'svelte';
	const i18n = getContext('i18n');

	import { settings } from '$lib/stores';
	import { verifyOpenAIConnection } from '$lib/apis/openai';
	import { verifyOllamaConnection } from '$lib/apis/ollama';

	import Modal from '$lib/components/common/Modal.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import Minus from '$lib/components/icons/Minus.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import Tags from './common/Tags.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import Textarea from './common/Textarea.svelte';

	export let onSubmit: Function = () => {};
	export let onDelete: Function = () => {};

	export let show = false;
	export let edit = false;

	export let ollama = false;
	export let direct = false;

	export let connection: any = null;

	let url = '';
	let key = '';
	let auth_type = 'bearer';
	let useKeyPool = false;
	let keyPoolKeys: string[] = [''];
	let keyStrategy = 'single';

	let connectionType = 'external';
	let provider = '';
	$: azure =
		provider === 'azure' ||
		((url.includes('azure.') || url.includes('cognitive.microsoft.com')) &&
			!direct &&
			provider === '' &&
			!/\/openai\/v1(\/|$)/.test(url));

	let prefixId = '';
	let enable = true;
	let apiVersion = '';
	let apiType = ''; // '' = chat completions (default), 'responses' = Responses API

	let headers = '';
	let additionalJson = '';
	let proxyType = 'http';
	let proxyInput = '';
	let proxies: string[] = [];

	let tags: Array<{ name: string } | string> = [];

	let modelId = '';
	let modelIds: string[] = [];

	let loading = false;
	let showDeleteConfirmDialog = false;

	const normalizeProxyList = (proxyList: unknown): string[] => {
		if (typeof proxyList === 'string') {
			const value = proxyList.trim();
			return value ? [value] : [];
		}

		if (!Array.isArray(proxyList)) {
			return [];
		}

		return proxyList
			.map((proxy) => (typeof proxy === 'string' ? proxy.trim() : ''))
			.filter(Boolean);
	};

	const normalizeKeyPool = (value: unknown): string[] => {
		if (Array.isArray(value)) {
			return value
				.map((item) => (typeof item === 'string' ? item : item?.key))
				.map((item) => `${item ?? ''}`.trim())
				.filter(Boolean);
		}

		return `${value ?? ''}`
			.split(/[\n,;]+/)
			.map((item) => item.trim())
			.filter(Boolean);
	};

	$: keyPool = normalizeKeyPool(keyPoolKeys);

	const addKeyPoolKey = () => {
		keyPoolKeys = [...keyPoolKeys, ''];
	};

	const removeKeyPoolKey = (idx: number) => {
		keyPoolKeys = keyPoolKeys.filter((_, keyIdx) => keyIdx !== idx);
		if (keyPoolKeys.length === 0) {
			keyPoolKeys = [''];
		}
	};

	const setKeyMode = (mode: 'single' | 'pool') => {
		useKeyPool = mode === 'pool';
	};

	const verifyOllamaHandler = async () => {
		// remove trailing slash from url
		url = url.replace(/\/$/, '');

		const res = await verifyOllamaConnection(localStorage.token, {
			url,
			key
		}).catch((error) => {
			toast.error(`${error}`);
		});

		if (res) {
			toast.success($i18n.t('Server connection verified'));
		}
	};

	const verifyOpenAIHandler = async () => {
		// remove trailing slash from url
		url = url.replace(/\/$/, '');

		let _headers = null;
		let _additionalJson = null;
		const normalizedProxies = normalizeProxyList(proxies);
		const normalizedKeyPool = !ollama && auth_type === 'bearer' && useKeyPool ? normalizeKeyPool(keyPoolKeys) : [];

		if (headers) {
			try {
				_headers = JSON.parse(headers);
				if (typeof _headers !== 'object' || Array.isArray(_headers)) {
					_headers = null;
					throw new Error('Headers must be a valid JSON object');
				}
				headers = JSON.stringify(_headers, null, 2);
			} catch (error) {
				toast.error($i18n.t('Headers must be a valid JSON object'));
				return;
			}
		}

		if (additionalJson) {
			try {
				_additionalJson = JSON.parse(additionalJson);
				if (
					typeof _additionalJson !== 'object' ||
					Array.isArray(_additionalJson) ||
					_additionalJson === null
				) {
					_additionalJson = null;
					throw new Error('Additional JSON must be a valid JSON object');
				}
				additionalJson = JSON.stringify(_additionalJson, null, 2);
			} catch (error) {
				toast.error($i18n.t('Additional JSON must be a valid JSON object'));
				return;
			}
		}

		const res = await verifyOpenAIConnection(
			localStorage.token,
			{
				url,
				key: auth_type === 'bearer' ? key || normalizedKeyPool[0] || '' : key,
				config: {
					auth_type,
					...(provider ? { provider } : {}),
					...(azure ? { azure: true } : {}),
					api_version: apiVersion,
					...(normalizedKeyPool.length > 0
						? {
								key_pool: normalizedKeyPool,
								key_strategy: keyStrategy
							}
						: {}),
					...(_headers ? { headers: _headers } : {}),
					...(_additionalJson ? { additional_json: _additionalJson } : {}),
					...(normalizedProxies.length > 0
						? {
								proxy_type: proxyType,
								proxies: normalizedProxies
							}
						: {})
				}
			},
			direct
		).catch((error) => {
			toast.error(`${error}`);
		});

		if (res) {
			toast.success($i18n.t('Server connection verified'));
		}
	};

	const verifyHandler = () => {
		if (ollama) {
			verifyOllamaHandler();
		} else {
			verifyOpenAIHandler();
		}
	};

	const addModelHandler = () => {
		if (modelId) {
			modelIds = [...modelIds, modelId];
			modelId = '';
		}
	};

	const addProxyHandler = () => {
		const trimmedProxy = proxyInput.trim();
		if (trimmedProxy) {
			proxies = [...proxies, trimmedProxy];
			proxyInput = '';
		}
	};

	const submitHandler = async () => {
		loading = true;

		if (!ollama && !url) {
			loading = false;
			toast.error($i18n.t('URL is required'));
			return;
		}

		const normalizedKeyPool = !ollama && auth_type === 'bearer' && useKeyPool ? normalizeKeyPool(keyPoolKeys) : [];

		if (!ollama && auth_type === 'bearer' && useKeyPool && normalizedKeyPool.length === 0) {
			loading = false;
			toast.error($i18n.t('Add at least one key or switch back to Single Key.'));
			return;
		}

		if (azure) {
			if (!apiVersion) {
				loading = false;

				toast.error($i18n.t('API Version is required'));
				return;
			}

			if (!key && normalizedKeyPool.length === 0 && !['azure_ad', 'microsoft_entra_id'].includes(auth_type)) {
				loading = false;

				toast.error($i18n.t('Key is required'));
				return;
			}

			if (modelIds.length === 0) {
				loading = false;
				toast.error($i18n.t('Deployment names are required for Azure OpenAI'));
				return;
			}
		}

		if (headers) {
			try {
				const _headers = JSON.parse(headers);
				if (typeof _headers !== 'object' || Array.isArray(_headers)) {
					throw new Error('Headers must be a valid JSON object');
				}
				headers = JSON.stringify(_headers, null, 2);
			} catch (error) {
				toast.error($i18n.t('Headers must be a valid JSON object'));
				loading = false;
				return;
			}
		}

		if (additionalJson) {
			try {
				const _additionalJson = JSON.parse(additionalJson);
				if (
					typeof _additionalJson !== 'object' ||
					Array.isArray(_additionalJson) ||
					_additionalJson === null
				) {
					throw new Error('Additional JSON must be a valid JSON object');
				}
				additionalJson = JSON.stringify(_additionalJson, null, 2);
			} catch (error) {
				toast.error($i18n.t('Additional JSON must be a valid JSON object'));
				loading = false;
				return;
			}
		}

		const normalizedProxies = normalizeProxyList(proxies);

		// remove trailing slash from url
		url = url.replace(/\/$/, '');

		const connection = {
			url,
			key: auth_type === 'bearer' ? key || normalizedKeyPool[0] || '' : key,
			config: {
				enable: enable,
				tags: tags,
				prefix_id: prefixId,
				model_ids: modelIds,
				connection_type: connectionType,
				auth_type,
				...(!ollama && normalizedKeyPool.length > 0
					? {
							key_pool: normalizedKeyPool,
							key_strategy: keyStrategy
						}
					: {}),
				headers: headers ? JSON.parse(headers) : undefined,
				additional_json: additionalJson ? JSON.parse(additionalJson) : undefined,
				...(normalizedProxies.length > 0
					? {
							proxy_type: proxyType,
							proxies: normalizedProxies
						}
					: {}),
				...(provider ? { provider } : {}),
				...(!ollama && azure ? { azure: true } : {}),
				...(azure ? { api_version: apiVersion } : {}),
				...(apiType ? { api_type: apiType } : {})
			}
		};

		await onSubmit(connection);

		loading = false;
		show = false;

		url = '';
		key = '';
		auth_type = 'bearer';
		useKeyPool = false;
		keyPoolKeys = [''];
		keyStrategy = 'single';
		prefixId = '';
		tags = [];
		modelIds = [];
		headers = '';
		additionalJson = '';
		proxyType = 'http';
		proxyInput = '';
		proxies = [];
	};

	const init = () => {
		if (connection) {
			url = connection.url;
			key = connection.key;

			auth_type = connection.config.auth_type ?? 'bearer';
			keyPoolKeys = normalizeKeyPool(connection.config?.key_pool);
			useKeyPool = keyPoolKeys.length > 0;
			if (keyPoolKeys.length === 0) {
				keyPoolKeys = [''];
			}
			keyStrategy = connection.config?.key_strategy ?? 'single';
			headers = connection.config?.headers
				? JSON.stringify(connection.config.headers, null, 2)
				: '';
			additionalJson = connection.config?.additional_json
				? JSON.stringify(connection.config.additional_json, null, 2)
				: '';
			proxyType = ['http', 'socks4', 'socks5'].includes(connection.config?.proxy_type)
				? connection.config?.proxy_type
				: 'http';
			proxies = normalizeProxyList(connection.config?.proxies ?? connection.config?.proxy);
			proxyInput = '';

			enable = connection.config?.enable ?? true;
			tags = connection.config?.tags ?? [];
			prefixId = connection.config?.prefix_id ?? '';
			modelIds = connection.config?.model_ids ?? [];

			if (ollama) {
				connectionType = connection.config?.connection_type ?? 'local';
			} else {
				connectionType = connection.config?.connection_type ?? 'external';
				provider = connection.config?.provider ?? (connection.config?.azure ? 'azure' : '');
				apiVersion = connection.config?.api_version ?? '';
				apiType = connection.config?.api_type ?? '';
			}
		} else {
			url = '';
			key = '';
			auth_type = 'bearer';
			useKeyPool = false;
			keyPoolKeys = [''];
			keyStrategy = 'single';
			enable = true;
			connectionType = ollama ? 'local' : 'external';
			azure = false;
			apiVersion = '';
			apiType = '';
			headers = '';
			additionalJson = '';
			proxyType = 'http';
			proxyInput = '';
			proxies = [];
			prefixId = '';
			tags = [];
			modelIds = [];
			modelId = '';
		}
	};

	$: if (show) {
		init();
	}

	onMount(() => {
		init();
	});
</script>

<Modal size="md" bind:show>
	<form
		class="flex max-h-[88dvh] flex-col dark:text-gray-200"
		on:submit={(e) => {
			e.preventDefault();
			submitHandler();
		}}
	>
		<div class="flex items-start justify-between gap-4 px-5 pt-5 pb-3 dark:text-gray-100">
			<div>
				<h1 class="font-primary text-lg font-medium">
					{#if edit}
						{$i18n.t('Edit Connection')}
					{:else}
						{$i18n.t('Add Connection')}
					{/if}
				</h1>
				<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
					{ollama ? $i18n.t('Configure an Ollama-compatible endpoint.') : $i18n.t('Configure an OpenAI-compatible endpoint.')}
				</div>
			</div>

			<button
				class="rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-850 dark:hover:text-gray-200"
				aria-label={$i18n.t('Close modal')}
				type="button"
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-5'} />
			</button>
		</div>

		<div class="flex-1 space-y-3 overflow-y-auto px-5 pb-4 scrollbar-hidden">
			<section class="space-y-3 rounded-xl border border-gray-100 dark:border-gray-850 p-3">
				<div class="flex items-center justify-between gap-3">
					<div>
						<div class="text-sm font-medium">{$i18n.t('Connection')}</div>
						<div class="text-xs text-gray-500 dark:text-gray-400">
							{$i18n.t('Endpoint, availability, and where the request is routed.')}
						</div>
					</div>
					<div class="flex items-center gap-3">
						{#if !direct}
							<div class="flex rounded-lg bg-gray-50 p-0.5 text-xs dark:bg-gray-850">
								<button
									type="button"
									class="rounded-md px-2.5 py-1 transition {connectionType === 'local'
										? 'bg-white text-gray-900 shadow-xs dark:bg-gray-700 dark:text-gray-100'
										: 'text-gray-500 dark:text-gray-400'}"
									on:click={() => {
										connectionType = 'local';
									}}
								>
									{$i18n.t('Local')}
								</button>
								<button
									type="button"
									class="rounded-md px-2.5 py-1 transition {connectionType === 'external'
										? 'bg-white text-gray-900 shadow-xs dark:bg-gray-700 dark:text-gray-100'
										: 'text-gray-500 dark:text-gray-400'}"
									on:click={() => {
										connectionType = 'external';
									}}
								>
									{$i18n.t('External')}
								</button>
							</div>
						{/if}

						<label class="sr-only" for="toggle-connection"
							>{$i18n.t('Toggle whether current connection is active.')}</label
						>
						<Tooltip content={enable ? $i18n.t('Enabled') : $i18n.t('Disabled')}>
							<Switch id="toggle-connection" bind:state={enable} />
						</Tooltip>
					</div>
				</div>

				<div class="grid gap-3 md:grid-cols-[1fr_auto]">
					<div>
						<label for="url-input" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
							>{$i18n.t('URL')}</label
						>
						<input
							id="url-input"
							class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden placeholder:text-gray-300 focus:border-gray-300 dark:border-gray-850 dark:placeholder:text-gray-700 dark:focus:border-gray-700"
							type="text"
							bind:value={url}
							placeholder={$i18n.t('API Base URL')}
							autocomplete="off"
							list={ollama ? undefined : 'suggestions'}
							required
						/>

						{#if !ollama}
							<datalist id="suggestions">
								<option value="https://api.openai.com/v1" />
								<option value="https://api.anthropic.com/v1" />
								<option value="https://generativelanguage.googleapis.com/v1beta/openai" />
								<option value="https://api.mistral.ai/v1" />
								<option value="https://api.groq.com/openai/v1" />
								<option value="https://openrouter.ai/api/v1" />
								<option value="https://api.x.ai/v1" />
							</datalist>
						{/if}
					</div>

					<Tooltip content={$i18n.t('Verify Connection')} className="self-end">
						<button
							class="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-100 bg-gray-50 text-gray-600 transition hover:bg-gray-100 dark:border-gray-850 dark:bg-gray-850 dark:text-gray-300 dark:hover:bg-gray-800"
							on:click={() => {
								verifyHandler();
							}}
							type="button"
							aria-label={$i18n.t('Verify Connection')}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 20 20"
								fill="currentColor"
								aria-hidden="true"
								class="h-4 w-4"
							>
								<path
									fill-rule="evenodd"
									d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z"
									clip-rule="evenodd"
								/>
							</svg>
						</button>
					</Tooltip>
				</div>
			</section>

			<section class="space-y-3 rounded-xl border border-gray-100 dark:border-gray-850 p-3">
				<div>
					<div class="text-sm font-medium">{$i18n.t('Authentication')}</div>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{#if useKeyPool}
							{$i18n.t('Use multiple API keys for this provider.')}
						{:else}
							{$i18n.t('Choose how requests authenticate with this endpoint.')}
						{/if}
					</div>
				</div>

				{#if !ollama}
					<div class="flex w-fit rounded-lg bg-gray-50 p-0.5 text-xs dark:bg-gray-850">
						<button
							type="button"
							class="rounded-md px-3 py-1.5 font-medium transition {!useKeyPool
								? 'bg-white text-gray-900 shadow-xs dark:bg-gray-700 dark:text-gray-100'
								: 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'}"
							on:click={() => setKeyMode('single')}
						>
							{$i18n.t('Single Key')}
						</button>
						<button
							type="button"
							class="rounded-md px-3 py-1.5 font-medium transition {useKeyPool
								? 'bg-white text-gray-900 shadow-xs dark:bg-gray-700 dark:text-gray-100'
								: 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'}"
							on:click={() => setKeyMode('pool')}
						>
							{$i18n.t('Key Pool')}
						</button>
					</div>
				{/if}

				{#if !useKeyPool}
					<div class="grid gap-3 md:grid-cols-[11rem_1fr]">
						<div>
							<label
								for="select-bearer-or-session"
								class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('Method')}</label
							>
							<select
								id="select-bearer-or-session"
								class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden dark:border-gray-850 dark:bg-gray-900"
								bind:value={auth_type}
							>
								<option value="none">{$i18n.t('None')}</option>
								<option value="bearer">{$i18n.t('Bearer')}</option>

								{#if !ollama}
									<option value="session">{$i18n.t('Session')}</option>
									{#if !direct}
										<option value="system_oauth">{$i18n.t('OAuth')}</option>
										<option value="microsoft_entra_id">{$i18n.t('Entra ID')}</option>
									{/if}
								{/if}
							</select>
						</div>

						<div>
							<label class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400">
								{auth_type === 'bearer' ? $i18n.t('API Key') : $i18n.t('Details')}
							</label>
							<div class="flex min-h-9 items-center rounded-lg border border-gray-100 px-3 dark:border-gray-850">
								{#if auth_type === 'bearer'}
									<SensitiveInput bind:value={key} placeholder={$i18n.t('API Key')} required={false} />
								{:else if auth_type === 'none'}
									<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('No authentication')}</div>
								{:else if auth_type === 'session'}
									<div class="text-xs text-gray-500 dark:text-gray-400">
										{$i18n.t('Forwards system user session credentials to authenticate')}
									</div>
								{:else if auth_type === 'system_oauth'}
									<div class="text-xs text-gray-500 dark:text-gray-400">
										{$i18n.t('Forwards system user OAuth access token to authenticate')}
									</div>
								{:else if ['azure_ad', 'microsoft_entra_id'].includes(auth_type)}
									<div class="text-xs text-gray-500 dark:text-gray-400">
										{$i18n.t('Uses DefaultAzureCredential to authenticate')}
									</div>
								{/if}
							</div>
						</div>
					</div>
				{:else}
					<div class="space-y-3">
						<div class="grid gap-3 md:grid-cols-[11rem_1fr]">
							<div>
								<label
									for="select-key-pool-method"
									class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
									>{$i18n.t('Method')}</label
								>
								<select
									id="select-key-pool-method"
									class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden dark:border-gray-850 dark:bg-gray-900"
									bind:value={auth_type}
								>
									<option value="none">{$i18n.t('None')}</option>
									<option value="bearer">{$i18n.t('Bearer')}</option>

									{#if !ollama}
										<option value="session">{$i18n.t('Session')}</option>
										{#if !direct}
											<option value="system_oauth">{$i18n.t('OAuth')}</option>
											<option value="microsoft_entra_id">{$i18n.t('Entra ID')}</option>
										{/if}
									{/if}
								</select>
							</div>

							<div>
								<label class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400">
									{auth_type === 'bearer' ? $i18n.t('API Key') : $i18n.t('Details')}
								</label>
								{#if auth_type === 'bearer'}
									<div class="space-y-2">
										{#each keyPoolKeys as poolKey, keyIdx}
											<div class="flex items-center gap-2">
												<div class="flex min-h-9 flex-1 items-center rounded-lg border border-gray-100 px-3 dark:border-gray-850">
													<SensitiveInput
														bind:value={keyPoolKeys[keyIdx]}
														placeholder={$i18n.t('API Key')}
														required={false}
													/>
												</div>

												{#if keyIdx === 0}
													<button
														type="button"
														class="inline-flex h-9 shrink-0 items-center gap-1 rounded-lg border border-gray-100 px-2.5 text-xs font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-850 dark:text-gray-200 dark:hover:bg-gray-850"
														on:click={addKeyPoolKey}
													>
														<Plus className="size-3.5" strokeWidth="2" />
														<span>{$i18n.t('Add a key')}</span>
													</button>
												{:else}
													<Tooltip content={$i18n.t('Remove key')}>
														<button
															type="button"
															class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-gray-100 text-gray-600 transition hover:bg-gray-50 dark:border-gray-850 dark:text-gray-300 dark:hover:bg-gray-850"
															aria-label={$i18n.t('Remove key')}
															on:click={() => {
																removeKeyPoolKey(keyIdx);
															}}
														>
															<Minus strokeWidth="2" className="size-3.5" />
														</button>
													</Tooltip>
												{/if}
											</div>
										{/each}
									</div>
								{:else}
									<div class="flex min-h-9 items-center rounded-lg border border-gray-100 px-3 dark:border-gray-850">
										{#if auth_type === 'none'}
											<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('No authentication')}</div>
										{:else if auth_type === 'session'}
											<div class="text-xs text-gray-500 dark:text-gray-400">
												{$i18n.t('Forwards system user session credentials to authenticate')}
											</div>
										{:else if auth_type === 'system_oauth'}
											<div class="text-xs text-gray-500 dark:text-gray-400">
												{$i18n.t('Forwards system user OAuth access token to authenticate')}
											</div>
										{:else if ['azure_ad', 'microsoft_entra_id'].includes(auth_type)}
											<div class="text-xs text-gray-500 dark:text-gray-400">
												{$i18n.t('Uses DefaultAzureCredential to authenticate')}
											</div>
										{/if}
									</div>
								{/if}
							</div>
						</div>

						{#if auth_type === 'bearer'}
							<div class="text-xs text-gray-500 dark:text-gray-400">
								{keyPool.length > 0
									? $i18n.t('{{COUNT}} key(s) ready', { COUNT: keyPool.length })
									: $i18n.t('Add at least one key or switch back to Single Key.')}
							</div>

							<div class="grid gap-2 md:grid-cols-[13rem_1fr]">
								<div>
									<label for="key-strategy-select" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400">
										{$i18n.t('Use keys by')}
									</label>
									<select
										id="key-strategy-select"
										class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden dark:border-gray-850 dark:bg-gray-900"
										bind:value={keyStrategy}
									>
										<option value="single">{$i18n.t('First key')}</option>
										<option value="random">{$i18n.t('Random key')}</option>
										<option value="sticky_until_failure">{$i18n.t('Same key until failure')}</option>
										<option value="switch_each_message">{$i18n.t('Switch each message')}</option>
									</select>
								</div>

								<div class="self-end rounded-lg bg-gray-50 p-2 text-xs text-gray-500 dark:bg-gray-850 dark:text-gray-400">
									{#if keyStrategy === 'random'}
										{$i18n.t('Every request picks a random key from the pool.')}
									{:else if keyStrategy === 'sticky_until_failure'}
										{$i18n.t('Requests keep using one key and move to the next after provider errors.')}
									{:else if keyStrategy === 'switch_each_message'}
										{$i18n.t('Requests rotate through the pool in order.')}
									{:else}
										{$i18n.t('Requests use the first available key.')}
									{/if}
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</section>

			<section class="space-y-3 rounded-xl border border-gray-100 dark:border-gray-850 p-3">
				<div>
					<div class="text-sm font-medium">{$i18n.t('Routing')}</div>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t('Provider behavior, model prefixes, and API compatibility.')}
					</div>
				</div>

				<div class="grid gap-3 md:grid-cols-2">
					<div>
						<label for="prefix-id-input" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
							>{$i18n.t('Prefix ID')}</label
						>
						<Tooltip
							content={$i18n.t(
								'Prefix ID is used to avoid conflicts with other connections by adding a prefix to the model IDs - leave empty to disable'
							)}
						>
							<input
								class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden placeholder:text-gray-300 focus:border-gray-300 dark:border-gray-850 dark:placeholder:text-gray-700 dark:focus:border-gray-700"
								type="text"
								id="prefix-id-input"
								bind:value={prefixId}
								placeholder={$i18n.t('Optional')}
								autocomplete="off"
							/>
						</Tooltip>
					</div>

					{#if !ollama && !direct}
						<div>
							<label for="provider-select" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('Provider')}</label
							>
							<select
								id="provider-select"
								bind:value={provider}
								class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden dark:border-gray-850 dark:bg-gray-900"
							>
								<option value="">{$i18n.t('Default')}</option>
								<option value="azure">{$i18n.t('Azure OpenAI')}</option>
								<option value="llama.cpp">{$i18n.t('llama.cpp')}</option>
							</select>
						</div>

						<div>
							<label for="api-type-toggle" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('API Type')}</label
							>
							<button
								on:click={() => {
									apiType = apiType === 'responses' ? '' : 'responses';
								}}
								type="button"
								id="api-type-toggle"
								class="flex w-full items-center justify-between rounded-lg border border-gray-100 px-3 py-2 text-left text-sm transition hover:bg-gray-50 dark:border-gray-850 dark:hover:bg-gray-850"
							>
								<span>
									{#if apiType === 'responses'}
										{$i18n.t('Responses')}
									{:else}
										{$i18n.t('Chat Completions')}
									{/if}
								</span>
								{#if apiType === 'responses'}
									<span class="text-xs text-gray-400 dark:text-gray-600">{$i18n.t('Experimental')}</span>
								{/if}
							</button>
						</div>
					{/if}

					{#if azure}
						<div>
							<label for="api-version-input" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('API Version')}</label
							>
							<input
								id="api-version-input"
								class="w-full rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden placeholder:text-gray-300 focus:border-gray-300 dark:border-gray-850 dark:placeholder:text-gray-700 dark:focus:border-gray-700"
								type="text"
								bind:value={apiVersion}
								placeholder={$i18n.t('API Version')}
								autocomplete="off"
								required
							/>
						</div>
					{/if}
				</div>
			</section>

			<section class="space-y-3 rounded-xl border border-gray-100 dark:border-gray-850 p-3">
				<div class="flex items-start justify-between gap-3">
					<div>
						<div class="text-sm font-medium">{$i18n.t('Models')}</div>
						<div class="text-xs text-gray-500 dark:text-gray-400">
							{#if ollama}
								{$i18n.t('Leave empty to include all models from "{{url}}/api/tags" endpoint', { url })}
							{:else if azure}
								{$i18n.t('Deployment names are required for Azure OpenAI')}
							{:else}
								{$i18n.t('Leave empty to include all models from "{{url}}/models" endpoint', { url })}
							{/if}
						</div>
					</div>
					<div class="shrink-0 text-xs text-gray-500 dark:text-gray-400">
						{modelIds.length > 0 ? $i18n.t('{{COUNT}} selected', { COUNT: modelIds.length }) : $i18n.t('All models')}
					</div>
				</div>

				{#if modelIds.length > 0}
					<ul class="flex flex-wrap gap-2">
						{#each modelIds as modelId, modelIdx}
							<li
								class="flex max-w-full items-center gap-1.5 rounded-lg bg-gray-50 px-2 py-1 text-xs dark:bg-gray-850"
							>
								<span class="truncate">{modelId}</span>
								<button
									aria-label={$i18n.t(`Remove {{MODELID}} from list.`, { MODELID: modelId })}
									type="button"
									class="shrink-0 rounded p-0.5 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
									on:click={() => {
										modelIds = modelIds.filter((_, idx) => idx !== modelIdx);
									}}
								>
									<Minus strokeWidth="2" className="size-3.5" />
								</button>
							</li>
						{/each}
					</ul>
				{/if}

				<div class="flex items-center gap-2">
					<label class="sr-only" for="add-model-id-input">{$i18n.t('Add a model ID')}</label>
					<input
						class="min-w-0 flex-1 rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden placeholder:text-gray-300 focus:border-gray-300 dark:border-gray-850 dark:placeholder:text-gray-700 dark:focus:border-gray-700"
						bind:value={modelId}
						id="add-model-id-input"
						placeholder={azure ? $i18n.t('Add a deployment name') : $i18n.t('Add a model ID')}
						on:keydown={(e) => {
							if (e.key === 'Enter') {
								e.preventDefault();
								addModelHandler();
							}
						}}
					/>

					<button
						type="button"
						class="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-100 text-gray-600 transition hover:bg-gray-50 dark:border-gray-850 dark:text-gray-300 dark:hover:bg-gray-850"
						aria-label={$i18n.t('Add')}
						on:click={() => {
							addModelHandler();
						}}
					>
						<Plus className="size-3.5" strokeWidth="2" />
					</button>
				</div>
			</section>

			<section class="space-y-3 rounded-xl border border-gray-100 dark:border-gray-850 p-3">
				<div>
					<div class="text-sm font-medium">{$i18n.t('Tags')}</div>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t('Labels for filtering and organizing model connections.')}
					</div>
				</div>

				<Tags
					bind:tags
					on:add={(e) => {
						tags = [
							...tags,
							{
								name: e.detail
							}
						];
					}}
					on:delete={(e) => {
						tags = tags.filter((tag) => (typeof tag === 'string' ? tag : tag.name) !== e.detail);
					}}
				/>
			</section>

			{#if !ollama && !direct}
				<section class="space-y-3 rounded-xl border border-gray-100 dark:border-gray-850 p-3">
					<div>
						<div class="text-sm font-medium">{$i18n.t('Advanced')}</div>
						<div class="text-xs text-gray-500 dark:text-gray-400">
							{$i18n.t('Optional headers, request body fields, and proxy overrides.')}
						</div>
					</div>

					<div class="grid gap-3 md:grid-cols-2">
						<div>
							<label for="headers-input" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('Headers')}</label
							>
							<Tooltip
								content={$i18n.t(
									'Enter additional headers in JSON format (e.g. {"X-Custom-Header": "value"}'
								)}
							>
								<Textarea
									className="w-full text-sm outline-hidden rounded-lg border border-gray-100 dark:border-gray-850 px-3 py-2"
									bind:value={headers}
									placeholder={$i18n.t('JSON object')}
									required={false}
									minSize={72}
								/>
							</Tooltip>
						</div>

						<div>
							<label
								for="additional-json-input"
								class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('Additional JSON')}</label
							>
							<Tooltip
								content={$i18n.t(
									'Enter additional request body fields in JSON format (merged into outgoing requests)'
								)}
							>
								<Textarea
									className="w-full text-sm outline-hidden rounded-lg border border-gray-100 dark:border-gray-850 px-3 py-2"
									bind:value={additionalJson}
									placeholder={$i18n.t('JSON object')}
									required={false}
									minSize={72}
								/>
							</Tooltip>
						</div>
					</div>

					<div>
						<div class="mb-1 flex items-center justify-between gap-3">
							<label for="proxy-type-input" class="text-xs font-medium text-gray-500 dark:text-gray-400"
								>{$i18n.t('Proxies')}</label
							>
							<select
								id="proxy-type-input"
								class="rounded-lg border border-gray-100 bg-transparent px-2 py-1 text-xs outline-hidden dark:border-gray-850 dark:bg-gray-900"
								bind:value={proxyType}
							>
								<option value="http">HTTP</option>
								<option value="socks4">SOCKS4</option>
								<option value="socks5">SOCKS5</option>
							</select>
						</div>

						{#if proxies.length > 0}
							<ul class="mb-2 flex flex-wrap gap-2">
								{#each proxies as proxyValue, proxyIdx}
									<li class="flex max-w-full items-center gap-1.5 rounded-lg bg-gray-50 px-2 py-1 text-xs dark:bg-gray-850">
										<span class="truncate">{proxyValue}</span>
										<button
											aria-label={$i18n.t(`Remove proxy {{PROXY}} from list.`, { PROXY: proxyValue })}
											type="button"
											class="shrink-0 rounded p-0.5 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
											on:click={() => {
												proxies = proxies.filter((_, idx) => idx !== proxyIdx);
											}}
										>
											<Minus strokeWidth="2" className="size-3.5" />
										</button>
									</li>
								{/each}
							</ul>
						{:else}
							<div class="mb-2 text-xs text-gray-500 dark:text-gray-400">
								{$i18n.t('Leave empty to use system/default proxy settings')}
							</div>
						{/if}

						<div class="flex items-center gap-2">
							<input
								class="min-w-0 flex-1 rounded-lg border border-gray-100 bg-transparent px-3 py-2 text-sm outline-hidden placeholder:text-gray-300 focus:border-gray-300 dark:border-gray-850 dark:placeholder:text-gray-700 dark:focus:border-gray-700"
								bind:value={proxyInput}
								placeholder={$i18n.t('Add proxy endpoint (host:port or URL)')}
								on:keydown={(e) => {
									if (e.key === 'Enter') {
										e.preventDefault();
										addProxyHandler();
									}
								}}
							/>
							<button
								type="button"
								class="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-100 text-gray-600 transition hover:bg-gray-50 dark:border-gray-850 dark:text-gray-300 dark:hover:bg-gray-850"
								aria-label={$i18n.t('Add')}
								on:click={() => {
									addProxyHandler();
								}}
							>
								<Plus className="size-3.5" strokeWidth="2" />
							</button>
						</div>
					</div>
				</section>
			{/if}
		</div>

		<div class="flex items-center justify-between border-t border-gray-100 px-5 py-4 text-sm font-medium dark:border-gray-850">
			<div>
				{#if edit}
					<button
						class="rounded-lg px-2 py-1.5 text-sm font-medium text-red-600 transition hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/30"
						type="button"
						on:click={() => {
							showDeleteConfirmDialog = true;
						}}
					>
						{$i18n.t('Delete')}
					</button>
				{/if}
			</div>

			<button
				class="flex items-center gap-2 rounded-full bg-black px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-900 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-white dark:text-black dark:hover:bg-gray-100"
				type="submit"
				disabled={loading}
			>
				{$i18n.t('Save')}

				{#if loading}
					<span class="shrink-0">
						<Spinner />
					</span>
				{/if}
			</button>
		</div>
	</form>
</Modal>

<ConfirmDialog
	bind:show={showDeleteConfirmDialog}
	message={$i18n.t(
		'Are you sure you want to delete this connection? This action cannot be undone.'
	)}
	confirmLabel={$i18n.t('Delete')}
	on:confirm={() => {
		onDelete();
		show = false;
	}}
/>
