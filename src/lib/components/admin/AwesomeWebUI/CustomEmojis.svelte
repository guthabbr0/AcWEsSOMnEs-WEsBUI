<script lang="ts">
	import { getContext, onDestroy, onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { toast } from 'svelte-sonner';

	import { getAdminConfig, updateAdminConfig } from '$lib/apis/auths';
	import { user } from '$lib/stores';
	import emojiShortCodes from '$lib/emoji-shortcodes.json';

	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');
	const t = (key: string, params?: Record<string, unknown>) => {
		const translator = get(i18n) as
			| { t?: (k: string, p?: Record<string, unknown>) => string }
			| undefined;
		return translator?.t ? translator.t(key, params) : key;
	};

	type CustomEmojiItem = {
		id: string;
		name: string;
		data_url: string;
		created_by?: string | null;
		created_by_name?: string | null;
		created_at?: number;
	};

	type CustomEmojiConfig = Record<string, unknown> & {
		CUSTOM_EMOJI_LIBRARY: CustomEmojiItem[];
	};

	let adminConfig: CustomEmojiConfig | null = null;
	let fileInputEl: HTMLInputElement;
	let autoSaveTimer: ReturnType<typeof setTimeout> | null = null;
	let autoSaveInFlight = false;
	let autoSaveQueued = false;
	let autoSaveReady = false;

	const standardShortCodes = new Set<string>(
		Object.values(emojiShortCodes)
			.flatMap((value) => (Array.isArray(value) ? value : [value]))
			.map((value) =>
				String(value ?? '')
					.trim()
					.toLowerCase()
			)
			.filter((value) => value.length > 0)
	);

	const sanitizeEmojiName = (value: string) =>
		String(value ?? '')
			.trim()
			.toLowerCase()
			.replace(/[^a-z0-9_]/g, '')
			.slice(0, 32);

	const createSafeId = () => {
		const cryptoObj = globalThis.crypto as Crypto | undefined;

		if (typeof cryptoObj?.randomUUID === 'function') {
			return cryptoObj.randomUUID();
		}

		if (cryptoObj?.getRandomValues) {
			const bytes = new Uint8Array(16);
			cryptoObj.getRandomValues(bytes);

			bytes[6] = (bytes[6] & 0x0f) | 0x40;
			bytes[8] = (bytes[8] & 0x3f) | 0x80;

			const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
			return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
		}

		return `emoji-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
	};

	const normalizeEmoji = (raw: unknown): CustomEmojiItem | null => {
		if (!raw || typeof raw !== 'object') {
			return null;
		}

		const emoji = raw as Partial<CustomEmojiItem>;
		const id = String(emoji.id ?? '').trim();
		const name = sanitizeEmojiName(String(emoji.name ?? ''));
		const dataUrl = String(emoji.data_url ?? '').trim();
		const createdBy = String(emoji.created_by ?? '').trim();
		const createdByName = String(emoji.created_by_name ?? '').trim();
		const createdAt = Number(emoji.created_at ?? Math.floor(Date.now() / 1000));

		if (!id || name.length < 2 || !dataUrl.startsWith('data:image/')) {
			return null;
		}

		return {
			id,
			name,
			data_url: dataUrl,
			created_by: createdBy || null,
			created_by_name: createdByName || null,
			created_at: Number.isFinite(createdAt) ? Math.floor(createdAt) : Math.floor(Date.now() / 1000)
		};
	};

	const normalizeAdminConfig = (configData: Record<string, unknown>): CustomEmojiConfig => ({
		...configData,
		CUSTOM_EMOJI_LIBRARY: Array.isArray(configData?.CUSTOM_EMOJI_LIBRARY)
			? configData.CUSTOM_EMOJI_LIBRARY.map((emoji) => normalizeEmoji(emoji)).filter(
					(item): item is CustomEmojiItem => item !== null
				)
			: []
	});

	const validateEmojiName = (name: string, ignoreId: string | null = null) => {
		if (name.length < 2) {
			toast.error(t('Emoji name must be at least 2 characters'));
			return false;
		}

		if (standardShortCodes.has(name)) {
			toast.error(t('This emoji name conflicts with a built-in emoji shortcode'));
			return false;
		}

		const duplicate = (adminConfig?.CUSTOM_EMOJI_LIBRARY ?? []).find(
			(emoji) => emoji.id !== ignoreId && emoji.name === name
		);
		if (duplicate) {
			toast.error(t('Emoji name must be unique'));
			return false;
		}

		return true;
	};

	const saveHandler = async (silent = false) => {
		if (!adminConfig) {
			return;
		}

		const sanitizedLibrary = adminConfig.CUSTOM_EMOJI_LIBRARY.map((emoji) =>
			normalizeEmoji(emoji)
		).filter((item): item is CustomEmojiItem => item !== null);

		const payload = {
			CUSTOM_EMOJI_LIBRARY: sanitizedLibrary
		};

		const response = await updateAdminConfig(localStorage.token, payload).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (response) {
			if (!silent) {
				adminConfig = normalizeAdminConfig(response);
			}
			if (!silent) {
				toast.success(t('Custom emojis updated'));
			}
		}
	};

	const runAutoSave = async () => {
		if (autoSaveInFlight) {
			autoSaveQueued = true;
			return;
		}

		autoSaveInFlight = true;
		await saveHandler(true);
		autoSaveInFlight = false;

		if (autoSaveQueued) {
			autoSaveQueued = false;
			await runAutoSave();
		}
	};

	const queueAutoSave = () => {
		if (!autoSaveReady || !adminConfig) {
			return;
		}

		if (autoSaveTimer) {
			clearTimeout(autoSaveTimer);
		}

		autoSaveTimer = setTimeout(() => {
			autoSaveTimer = null;
			void runAutoSave();
		}, 800);
	};

	const readFileAsDataUrl = (file: File): Promise<string> =>
		new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = (event) => resolve(String(event.target?.result ?? ''));
			reader.onerror = (error) => reject(error);
			reader.readAsDataURL(file);
		});

	const getAvailableEmojiName = (baseName: string, usedNames: Set<string>) => {
		let seed = sanitizeEmojiName(baseName);
		if (seed.length < 2) {
			seed = 'emoji';
		}

		let candidate = seed;
		let suffix = 2;

		while (standardShortCodes.has(candidate) || usedNames.has(candidate)) {
			const suffixText = `_${suffix}`;
			const trimmedSeed = seed.slice(0, Math.max(2, 32 - suffixText.length));
			candidate = `${trimmedSeed}${suffixText}`;
			suffix += 1;
		}

		return candidate;
	};

	const uploadEmojiHandler = async (fileList: FileList | null) => {
		if (!adminConfig || !fileList?.length) {
			return;
		}

		const files = Array.from(fileList);
		const usedNames = new Set(
			(adminConfig.CUSTOM_EMOJI_LIBRARY ?? []).map((emoji) => sanitizeEmojiName(emoji.name))
		);

		const nextEmojis: CustomEmojiItem[] = [];
		let addedCount = 0;
		let failedCount = 0;

		for (const file of files) {
			if (!file.type.startsWith('image/')) {
				failedCount += 1;
				continue;
			}

			// Keep payload size practical for persistent config storage.
			if (file.size > 1024 * 1024) {
				failedCount += 1;
				continue;
			}

			const dataUrl = await readFileAsDataUrl(file).catch(() => '');
			if (!dataUrl.startsWith('data:image/')) {
				failedCount += 1;
				continue;
			}

			const baseName = file.name.replace(/\.[^.]+$/, '');
			const name = getAvailableEmojiName(baseName, usedNames);
			usedNames.add(name);

			nextEmojis.push({
				id: createSafeId(),
				name,
				data_url: dataUrl,
				created_by: $user?.id ?? null,
				created_by_name: $user?.name ?? null,
				created_at: Math.floor(Date.now() / 1000)
			});
			addedCount += 1;
		}

		if (addedCount > 0) {
			adminConfig.CUSTOM_EMOJI_LIBRARY = [...adminConfig.CUSTOM_EMOJI_LIBRARY, ...nextEmojis];
			queueAutoSave();
			toast.success(
				t('{{COUNT}} emoji uploaded', {
					COUNT: addedCount
				})
			);
		}

		if (failedCount > 0) {
			toast.error(
				t('{{COUNT}} file(s) failed to upload', {
					COUNT: failedCount
				})
			);
		}
	};

	const renameEmoji = (emojiId: string, rawName: string) => {
		if (!adminConfig) {
			return false;
		}

		const nextName = sanitizeEmojiName(rawName);
		if (!validateEmojiName(nextName, emojiId)) {
			return false;
		}

		adminConfig.CUSTOM_EMOJI_LIBRARY = adminConfig.CUSTOM_EMOJI_LIBRARY.map((emoji) =>
			emoji.id === emojiId ? { ...emoji, name: nextName } : emoji
		);
		queueAutoSave();
		return true;
	};

	const removeEmoji = (emojiId: string) => {
		if (!adminConfig) {
			return;
		}

		adminConfig.CUSTOM_EMOJI_LIBRARY = adminConfig.CUSTOM_EMOJI_LIBRARY.filter(
			(emoji) => emoji.id !== emojiId
		);
		queueAutoSave();
	};

	const formatTimestamp = (value?: number) => {
		if (!value) {
			return t('Unknown');
		}

		const date = new Date(value * 1000);
		if (Number.isNaN(date.getTime())) {
			return t('Unknown');
		}
		return date.toLocaleString();
	};

	onMount(async () => {
		const configResponse = await getAdminConfig(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (configResponse) {
			adminConfig = normalizeAdminConfig(configResponse);
		}

		autoSaveReady = true;
	});

	onDestroy(() => {
		if (autoSaveTimer) {
			clearTimeout(autoSaveTimer);
			autoSaveTimer = null;
			void runAutoSave();
		}
	});
</script>

<form
	class="flex h-full flex-col justify-between text-sm"
	on:submit|preventDefault={() => {
		saveHandler();
	}}
>
	<div class="h-full space-y-3 overflow-y-scroll scrollbar-hidden pr-1">
		{#if adminConfig}
			<section class="rounded-xl border border-gray-100 dark:border-gray-850 p-3 space-y-3">
				<div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
					<div>
						<div class="text-base font-medium">{$i18n.t('Custom Emojis')}</div>
						<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
							{$i18n.t('Upload server-wide custom emoji that users can use in statuses, reactions, and emoji pickers.')}
						</div>
					</div>
					<div class="flex shrink-0 items-center gap-2">
						<span class="rounded-lg bg-gray-50 px-2 py-1 text-xs text-gray-500 dark:bg-gray-850 dark:text-gray-400">
							{adminConfig.CUSTOM_EMOJI_LIBRARY.length} {$i18n.t('emoji')}
						</span>
						<button
							type="button"
							class="rounded-full bg-black px-3 py-2 text-xs font-medium text-white transition hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100"
							on:click={() => fileInputEl?.click()}
						>
							{$i18n.t('Upload image')}
						</button>
					</div>

					<input
						bind:this={fileInputEl}
						type="file"
						accept="image/*"
						multiple
						class="hidden"
						on:change={(event) => {
							const target = event.currentTarget as HTMLInputElement;
							uploadEmojiHandler(target.files);
							target.value = '';
						}}
					/>
				</div>
				<div class="text-[11px] text-gray-500 dark:text-gray-400">
					{$i18n.t('Supported: image/* (PNG, JPG, WEBP, GIF), max 1 MB. Names are generated from file names.')}
				</div>
			</section>

			<section class="space-y-1">
					{#if adminConfig.CUSTOM_EMOJI_LIBRARY.length === 0}
					<div class="rounded-xl border border-gray-100 p-4 text-xs text-gray-500 dark:border-gray-850 dark:text-gray-400">
							{$i18n.t('No custom emojis uploaded yet.')}
						</div>
					{:else}
							{#each adminConfig.CUSTOM_EMOJI_LIBRARY as emoji (emoji.id)}
								<div
								class="grid gap-3 border-b border-gray-100 px-2 py-2 last:border-b-0 dark:border-gray-850 md:grid-cols-[3rem_minmax(0,1fr)_minmax(9rem,14rem)_auto] md:items-center"
								>
								<div class="flex items-center gap-3 md:block">
									<div class="flex size-11 items-center justify-center rounded-lg bg-gray-50 dark:bg-gray-950/60">
											<img
												src={emoji.data_url}
												alt={emoji.name}
											class="max-h-9 max-w-9 rounded object-contain"
												loading="lazy"
											/>
										</div>
								</div>

										<div class="space-y-1">
									<label class="sr-only" for="emoji-name-{emoji.id}">{$i18n.t('Emoji name')}</label>
											<input
										id="emoji-name-{emoji.id}"
												type="text"
												value={emoji.name}
												on:change={(event) => {
													const target = event.currentTarget as HTMLInputElement;
													if (!renameEmoji(emoji.id, target.value)) {
														target.value = emoji.name;
													}
												}}
										class="w-full rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850"
											/>
											<div class="text-[11px] text-gray-500 dark:text-gray-400">
												:{emoji.name}:
											</div>
										</div>

										<div class="text-[11px] text-gray-500 dark:text-gray-400">
									<div class="truncate">
										{emoji.created_by_name || emoji.created_by || 'Unknown'}
											</div>
									<div class="truncate">
										{formatTimestamp(emoji.created_at)}
											</div>
										</div>

								<div class="flex items-center gap-1 md:justify-end">
									<button
										type="button"
										class="rounded-lg p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-850 dark:hover:text-gray-200"
										aria-label={$i18n.t('Copy shortcode')}
										on:click={() => {
											navigator.clipboard.writeText(`:${emoji.name}:`);
											toast.success(t('Copied'));
										}}
									>
										<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
											<path d="M7 3.5A1.5 1.5 0 0 1 8.5 2h6A1.5 1.5 0 0 1 16 3.5v8A1.5 1.5 0 0 1 14.5 13h-6A1.5 1.5 0 0 1 7 11.5v-8Z" />
											<path d="M4 6.5A1.5 1.5 0 0 1 5.5 5H6v6.5A2.5 2.5 0 0 0 8.5 14H13v.5a1.5 1.5 0 0 1-1.5 1.5h-6A1.5 1.5 0 0 1 4 14.5v-8Z" />
										</svg>
									</button>
											<button
												type="button"
										class="rounded-lg p-2 text-red-500 transition hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950/40"
										aria-label={$i18n.t('Remove')}
												on:click={() => removeEmoji(emoji.id)}
											>
										<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
											<path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75V4.5H3.75a.75.75 0 0 0 0 1.5h.3l.72 9.43A3 3 0 0 0 7.76 18h4.48a3 3 0 0 0 2.99-2.57L15.95 6h.3a.75.75 0 0 0 0-1.5H14v-.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM7.5 4.5v-.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.75h-5Z" clip-rule="evenodd" />
										</svg>
											</button>
										</div>
								</div>
							{/each}
					{/if}
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
