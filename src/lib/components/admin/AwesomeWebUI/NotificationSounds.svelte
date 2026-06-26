<script lang="ts">
	import { getContext, onDestroy, onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { toast } from 'svelte-sonner';

	import { getAdminConfig, updateAdminConfig } from '$lib/apis/auths';

	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');
	const t = (key: string, params?: Record<string, unknown>) => {
		const translator = get(i18n) as
			| { t?: (k: string, p?: Record<string, unknown>) => string }
			| undefined;
		return translator?.t ? translator.t(key, params) : key;
	};

	type SoundType = 'channel' | 'chat_completion';

	type NotificationSoundItem = {
		id: string;
		name: string;
		type: SoundType;
		data_url: string;
	};

	type NotificationSoundConfig = Record<string, unknown> & {
		NOTIFICATION_SOUND_LIBRARY: NotificationSoundItem[];
	};

	let adminConfig: NotificationSoundConfig | null = null;
	let pendingType: SoundType = 'channel';
	let fileInputEl: HTMLInputElement;

	let autoSaveTimer: ReturnType<typeof setTimeout> | null = null;
	let autoSaveInFlight = false;
	let autoSaveQueued = false;
	let autoSaveReady = false;
	let playingSoundId: string | null = null;
	let soundProgress: Record<string, number> = {};
	let soundDurations: Record<string, number> = {};

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

		return `sound-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
	};

	const normalizeSound = (raw: unknown): NotificationSoundItem | null => {
		if (!raw || typeof raw !== 'object') {
			return null;
		}

		const sound = raw as Partial<NotificationSoundItem>;
		const id = String(sound.id ?? '').trim();
		const name = String(sound.name ?? '').trim();
		const type = String(sound.type ?? '')
			.trim()
			.toLowerCase();
		const dataUrl = String(sound.data_url ?? '').trim();

		if (!id || !name || !dataUrl.startsWith('data:audio/')) {
			return null;
		}
		if (!['channel', 'chat_completion'].includes(type)) {
			return null;
		}

		return {
			id,
			name,
			type: type as SoundType,
			data_url: dataUrl
		};
	};

	const normalizeAdminConfig = (configData: Record<string, unknown>): NotificationSoundConfig => ({
		...configData,
		NOTIFICATION_SOUND_LIBRARY: Array.isArray(configData?.NOTIFICATION_SOUND_LIBRARY)
			? configData.NOTIFICATION_SOUND_LIBRARY.map((item) => normalizeSound(item)).filter(
					(item): item is NotificationSoundItem => item !== null
				)
			: []
	});

	const saveHandler = async (silent = false) => {
		if (!adminConfig) {
			return;
		}

		const payload = {
			NOTIFICATION_SOUND_LIBRARY: adminConfig.NOTIFICATION_SOUND_LIBRARY
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
				toast.success(t('Notification sounds updated'));
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

	const updateSoundName = (soundId: string, name: string) => {
		if (!adminConfig) {
			return;
		}

		adminConfig.NOTIFICATION_SOUND_LIBRARY = adminConfig.NOTIFICATION_SOUND_LIBRARY.map((sound) =>
			sound.id === soundId ? { ...sound, name } : sound
		);
		queueAutoSave();
	};

	const updateSoundType = (soundId: string, type: SoundType) => {
		if (!adminConfig) {
			return;
		}

		adminConfig.NOTIFICATION_SOUND_LIBRARY = adminConfig.NOTIFICATION_SOUND_LIBRARY.map((sound) =>
			sound.id === soundId ? { ...sound, type } : sound
		);
		queueAutoSave();
	};

	const readFileAsDataUrl = (file: File): Promise<string> => {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = (event) => {
				resolve(String(event.target?.result ?? ''));
			};
			reader.onerror = (error) => {
				reject(error);
			};
			reader.readAsDataURL(file);
		});
	};

	const uploadSoundHandler = async (fileList: FileList | null) => {
		if (!adminConfig || !fileList?.length) {
			return;
		}

		const files = Array.from(fileList);
		const nextSounds: NotificationSoundItem[] = [];
		let addedCount = 0;
		let failedCount = 0;

		for (const file of files) {
			if (!file.type.startsWith('audio/')) {
				failedCount += 1;
				continue;
			}

			// Keep config payload practical for DB persistence and realtime sync.
			if (file.size > 2 * 1024 * 1024) {
				failedCount += 1;
				continue;
			}

			const dataUrl = await readFileAsDataUrl(file).catch(() => '');
			if (!dataUrl.startsWith('data:audio/')) {
				failedCount += 1;
				continue;
			}

			nextSounds.push({
				id: createSafeId(),
				name: file.name.replace(/\.[^.]+$/, ''),
				type: pendingType,
				data_url: dataUrl
			});
			addedCount += 1;
		}

		if (addedCount > 0) {
			adminConfig.NOTIFICATION_SOUND_LIBRARY = [
				...adminConfig.NOTIFICATION_SOUND_LIBRARY,
				...nextSounds
			];
			queueAutoSave();
			toast.success(
				t('{{COUNT}} sound(s) uploaded', {
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

	const removeSound = (soundId: string) => {
		if (!adminConfig) {
			return;
		}

		if (playingSoundId === soundId) {
			playingSoundId = null;
		}
		adminConfig.NOTIFICATION_SOUND_LIBRARY = adminConfig.NOTIFICATION_SOUND_LIBRARY.filter(
			(sound) => sound.id !== soundId
		);
		queueAutoSave();
	};

	const getAudioElement = (soundId: string) =>
		document.getElementById(`notification-sound-${soundId}`) as HTMLAudioElement | null;

	const formatAudioTime = (value: number | undefined) => {
		if (!Number.isFinite(value ?? NaN) || !value) {
			return '0:00';
		}

		const seconds = Math.max(0, Math.floor(value));
		return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
	};

	const pauseOtherSounds = (soundId: string) => {
		for (const sound of adminConfig?.NOTIFICATION_SOUND_LIBRARY ?? []) {
			if (sound.id === soundId) {
				continue;
			}

			getAudioElement(sound.id)?.pause();
		}
	};

	const toggleSoundPlayback = async (soundId: string) => {
		const audio = getAudioElement(soundId);
		if (!audio) {
			return;
		}

		if (!audio.paused) {
			audio.pause();
			playingSoundId = null;
			return;
		}

		pauseOtherSounds(soundId);
		await audio.play().catch((error) => {
			toast.error(`${error}`);
		});
		if (!audio.paused) {
			playingSoundId = soundId;
		}
	};

	const updateSoundProgress = (soundId: string) => {
		const audio = getAudioElement(soundId);
		if (!audio) {
			return;
		}

		soundProgress = {
			...soundProgress,
			[soundId]: audio.currentTime
		};
		soundDurations = {
			...soundDurations,
			[soundId]: Number.isFinite(audio.duration) ? audio.duration : 0
		};
	};

	const seekSound = (soundId: string, value: string) => {
		const audio = getAudioElement(soundId);
		if (!audio) {
			return;
		}

		audio.currentTime = Number(value);
		updateSoundProgress(soundId);
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
					<div class="text-base font-medium">{$i18n.t('Notification Sounds')}</div>
						<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t(
							'Upload custom sounds for channels and chat completions. Users can choose defaults and per-channel overrides.'
						)}
						</div>
					</div>
					<div class="flex shrink-0 items-center gap-2">
						<select
							class="rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850 dark:bg-gray-900"
							bind:value={pendingType}
						>
							<option value="channel">{$i18n.t('Channel notifications')}</option>
							<option value="chat_completion">{$i18n.t('Chat completion')}</option>
						</select>

						<button
							type="button"
							class="rounded-full bg-black px-3 py-2 text-xs font-medium text-white transition hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100"
							on:click={() => fileInputEl?.click()}
						>
							{$i18n.t('Upload audio')}
						</button>
					</div>

					<input
						bind:this={fileInputEl}
						type="file"
						accept="audio/*"
						multiple
						class="hidden"
						on:change={(event) => {
							const target = event.currentTarget as HTMLInputElement;
							uploadSoundHandler(target.files);
							target.value = '';
						}}
					/>
				</div>

				<div class="text-[11px] text-gray-500 dark:text-gray-400">
					{$i18n.t('Supported: audio/*, max size 2 MB per file')}
				</div>
			</section>

			<section class="space-y-2">
					{#if adminConfig.NOTIFICATION_SOUND_LIBRARY.length === 0}
					<div class="rounded-xl border border-gray-100 p-4 text-xs text-gray-500 dark:border-gray-850 dark:text-gray-400">
							{$i18n.t('No custom sounds uploaded yet.')}
						</div>
					{:else}
							{#each adminConfig.NOTIFICATION_SOUND_LIBRARY as sound (sound.id)}
								<div
								class="rounded-xl border border-gray-100 bg-white/50 p-3 dark:border-gray-850 dark:bg-gray-900/30"
								>
								<div class="flex flex-col gap-2">
									<div class="flex items-start gap-3">
										<div
											class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/40 dark:text-indigo-300"
										>
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
												<path d="M9.383 3.076A1 1 0 0 1 10 4v12a1 1 0 0 1-1.617.787L4.936 14H3a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h1.936l3.447-2.787a1 1 0 0 1 1-.137ZM14.657 5.757a1 1 0 0 1 1.414 0A6 6 0 0 1 18 10a6 6 0 0 1-1.929 4.243a1 1 0 0 1-1.414-1.414A4 4 0 0 0 16 10a4 4 0 0 0-1.343-2.829a1 1 0 0 1 0-1.414Z" />
												<path d="M12.536 7.879a1 1 0 0 1 1.415 0A3 3 0 0 1 15 10a3 3 0 0 1-1.05 2.121a1 1 0 1 1-1.414-1.414A1 1 0 0 0 13 10a1 1 0 0 0-.464-.707a1 1 0 0 1 0-1.414Z" />
											</svg>
										</div>

										<div class="min-w-0 flex-1 space-y-2">
											<div class="grid gap-2 sm:grid-cols-[1fr_auto]">
										<input
											type="text"
											value={sound.name}
											on:input={(event) => {
												updateSoundName(sound.id, event.currentTarget.value);
											}}
													class="min-w-0 rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850"
										/>
										<select
													class="rounded-lg border border-gray-100 bg-transparent px-2.5 py-2 text-xs outline-hidden dark:border-gray-850 dark:bg-gray-900"
											value={sound.type}
											on:change={(event) => {
												updateSoundType(sound.id, event.currentTarget.value as SoundType);
											}}
										>
											<option value="channel">{$i18n.t('Channel notifications')}</option>
											<option value="chat_completion">{$i18n.t('Chat completion')}</option>
										</select>
											</div>

											<div class="flex items-center gap-2 rounded-lg bg-gray-50 px-2 py-1.5 dark:bg-gray-950/40">
												<button
													type="button"
													class="flex size-7 shrink-0 items-center justify-center rounded-md bg-gray-900 text-white transition hover:bg-gray-700 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-white"
													aria-label={playingSoundId === sound.id ? $i18n.t('Pause') : $i18n.t('Play')}
													on:click={() => toggleSoundPlayback(sound.id)}
												>
													{#if playingSoundId === sound.id}
														<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
															<path d="M6.5 5A1.5 1.5 0 0 0 5 6.5v7A1.5 1.5 0 0 0 6.5 15h.5A1.5 1.5 0 0 0 8.5 13.5v-7A1.5 1.5 0 0 0 7 5h-.5ZM13 5a1.5 1.5 0 0 0-1.5 1.5v7A1.5 1.5 0 0 0 13 15h.5A1.5 1.5 0 0 0 15 13.5v-7A1.5 1.5 0 0 0 13.5 5H13Z" />
														</svg>
													{:else}
														<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
															<path d="M6.3 2.84A1.5 1.5 0 0 0 4 4.11v11.78a1.5 1.5 0 0 0 2.3 1.27l9.35-5.89a1.5 1.5 0 0 0 0-2.54L6.3 2.84Z" />
														</svg>
													{/if}
												</button>

												<div class="w-16 shrink-0 text-[11px] font-medium tabular-nums text-gray-600 dark:text-gray-300">
													{formatAudioTime(soundProgress[sound.id])}/{formatAudioTime(soundDurations[sound.id])}
												</div>

												<input
													type="range"
													min="0"
													max={soundDurations[sound.id] || 0}
													step="0.01"
													value={soundProgress[sound.id] || 0}
													class="h-1 min-w-0 flex-1 accent-gray-900 dark:accent-gray-100"
													aria-label={$i18n.t('Seek')}
													on:input={(event) => seekSound(sound.id, event.currentTarget.value)}
												/>

												<a
													href={sound.data_url}
													download={`${sound.name}.mp3`}
													class="rounded-md p-1.5 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-850 dark:hover:text-gray-200"
													aria-label={$i18n.t('Download')}
												>
													<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
														<path d="M10.75 2.75a.75.75 0 0 0-1.5 0v8.69L6.03 8.22a.75.75 0 0 0-1.06 1.06l4.5 4.5a.75.75 0 0 0 1.06 0l4.5-4.5a.75.75 0 0 0-1.06-1.06l-3.22 3.22V2.75Z" />
														<path d="M3.5 13.75a.75.75 0 0 0-1.5 0v.5A2.75 2.75 0 0 0 4.75 17h10.5A2.75 2.75 0 0 0 18 14.25v-.5a.75.75 0 0 0-1.5 0v.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-.5Z" />
													</svg>
												</a>

										<button
											type="button"
													class="rounded-md p-1.5 text-red-500 transition hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950/40"
											on:click={() => removeSound(sound.id)}
													aria-label={$i18n.t('Remove')}
										>
													<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-4" aria-hidden="true">
														<path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75V4.5H3.75a.75.75 0 0 0 0 1.5h.3l.72 9.43A3 3 0 0 0 7.76 18h4.48a3 3 0 0 0 2.99-2.57L15.95 6h.3a.75.75 0 0 0 0-1.5H14v-.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM7.5 4.5v-.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.75h-5Z" clip-rule="evenodd" />
													</svg>
										</button>
											</div>

											<audio
												id="notification-sound-{sound.id}"
												src={sound.data_url}
												preload="metadata"
												class="hidden"
												on:loadedmetadata={() => updateSoundProgress(sound.id)}
												on:timeupdate={() => updateSoundProgress(sound.id)}
												on:ended={() => {
													playingSoundId = null;
													updateSoundProgress(sound.id);
												}}
												on:pause={() => {
													if (playingSoundId === sound.id) {
														playingSoundId = null;
													}
												}}
											></audio>
											</div>
										</div>
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
