<script lang="ts">
	import { formatFileSize } from '$lib/utils';

	export let src = '';
	export let name = '';
	export let size: number | null = null;
	export let contentType = '';

	let audioElement: HTMLAudioElement;
	let currentTime = 0;
	let duration = 0;
	let volume = 1;
	let playing = false;

	const decodeString = (value: string) => {
		try {
			return decodeURIComponent(value);
		} catch {
			return value;
		}
	};

	const formatTime = (value: number) => {
		if (!Number.isFinite(value) || value <= 0) {
			return '0:00';
		}

		const minutes = Math.floor(value / 60);
		const seconds = Math.floor(value % 60)
			.toString()
			.padStart(2, '0');
		return `${minutes}:${seconds}`;
	};

	const togglePlayback = async () => {
		if (!audioElement) {
			return;
		}

		if (!audioElement.paused) {
			audioElement.pause();
			playing = false;
			return;
		}

		await audioElement.play().catch(() => {
			playing = false;
		});
		playing = !audioElement.paused;
	};

	const updateProgress = () => {
		if (!audioElement) {
			return;
		}

		currentTime = audioElement.currentTime || 0;
		duration = Number.isFinite(audioElement.duration) ? audioElement.duration : 0;
	};

	const seek = (value: number) => {
		if (!audioElement) {
			return;
		}

		audioElement.currentTime = value;
		currentTime = value;
	};

	const setVolume = (value: number) => {
		volume = Math.min(1, Math.max(0, value));
		if (audioElement) {
			audioElement.volume = volume;
		}
	};
</script>

<div
	class="w-full min-w-[18rem] max-w-xl border border-gray-200/70 bg-white/90 p-3 shadow-sm dark:border-gray-800/80 dark:bg-gray-900/80"
>
	<div class="mb-3 flex items-start gap-3">
		<div
			class="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-700 dark:bg-blue-500/15 dark:text-blue-300"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
				class="size-5"
				aria-hidden="true"
			>
				<path
					d="M8.25 6.75A2.25 2.25 0 0 1 10.5 4.5h3A2.25 2.25 0 0 1 15.75 6.75v6.856a3.75 3.75 0 1 1-1.5-3.005V6.75a.75.75 0 0 0-.75-.75h-3a.75.75 0 0 0-.75.75v8.856a3.75 3.75 0 1 1-1.5-3.005V6.75Z"
				/>
			</svg>
		</div>

		<div class="min-w-0 flex-1">
			<div class="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
				{decodeString(name) || 'Audio file'}
			</div>

			<div class="mt-0.5 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
				{#if size !== null}
					<span>{formatFileSize(size)}</span>
				{/if}

				{#if contentType}
					<span class="truncate">{contentType}</span>
				{/if}
			</div>
		</div>
	</div>

	<div class="flex items-center gap-2 bg-gray-50 px-2 py-1.5 dark:bg-black/30">
		<button
			type="button"
			class="flex size-7 shrink-0 items-center justify-center rounded text-gray-700 transition hover:bg-gray-200 dark:text-gray-200 dark:hover:bg-gray-800"
			aria-label={playing ? 'Pause' : 'Play'}
			on:click={togglePlayback}
		>
			{#if playing}
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5" aria-hidden="true">
					<path d="M6.25 3A1.25 1.25 0 0 0 5 4.25v11.5a1.25 1.25 0 1 0 2.5 0V4.25A1.25 1.25 0 0 0 6.25 3Zm7.5 0A1.25 1.25 0 0 0 12.5 4.25v11.5a1.25 1.25 0 1 0 2.5 0V4.25A1.25 1.25 0 0 0 13.75 3Z" />
				</svg>
			{:else}
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5" aria-hidden="true">
					<path d="M5.25 3.5A1.5 1.5 0 0 1 7.5 2.2l8.25 5.25a1.5 1.5 0 0 1 0 2.6L7.5 15.3a1.5 1.5 0 0 1-2.25-1.3V3.5Z" />
				</svg>
			{/if}
		</button>

		<div class="shrink-0 font-mono text-[11px] font-semibold text-gray-700 dark:text-gray-200">
			{formatTime(currentTime)}/{formatTime(duration)}
		</div>

		<input
			class="h-1 min-w-0 flex-1 accent-pink-400"
			type="range"
			min="0"
			max={duration || 0}
			step="0.01"
			value={currentTime}
			aria-label="Seek audio"
			on:input={(event) => seek(Number(event.currentTarget.value))}
		/>

		<div class="flex shrink-0 items-center gap-1">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5 text-gray-700 dark:text-gray-200" aria-hidden="true">
				<path d="M9.38 3.08A1 1 0 0 1 10 4v12a1 1 0 0 1-1.62.78L5.7 14.64H3.5A1.5 1.5 0 0 1 2 13.14V6.86a1.5 1.5 0 0 1 1.5-1.5h2.2l2.68-2.28Z" />
				<path d="M13.12 6.46a.75.75 0 0 1 1.06 0 5 5 0 0 1 0 7.08.75.75 0 0 1-1.06-1.06 3.5 3.5 0 0 0 0-4.96.75.75 0 0 1 0-1.06Z" />
				<path d="M15.24 4.34a.75.75 0 0 1 1.06 0 8 8 0 0 1 0 11.32.75.75 0 0 1-1.06-1.06 6.5 6.5 0 0 0 0-9.2.75.75 0 0 1 0-1.06Z" />
			</svg>
			<input
				class="h-1 w-16 accent-pink-400"
				type="range"
				min="0"
				max="1"
				step="0.01"
				value={volume}
				aria-label="Audio volume"
				on:input={(event) => setVolume(Number(event.currentTarget.value))}
			/>
		</div>
	</div>

	<audio
		bind:this={audioElement}
		preload="metadata"
		on:loadedmetadata={updateProgress}
		on:timeupdate={updateProgress}
		on:play={() => (playing = true)}
		on:pause={() => (playing = false)}
		on:ended={() => {
			playing = false;
			updateProgress();
		}}
	>
		<source {src} type={contentType || undefined} />
	</audio>
</div>
