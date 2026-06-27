<script>
	import { getContext } from 'svelte';
	import { onDestroy, onMount } from 'svelte';
	const i18n = getContext('i18n');
	import WebSearchResults from '../WebSearchResults.svelte';
	import Search from '$lib/components/icons/Search.svelte';

	export let status = null;
	export let done = false;

	let now = Date.now();
	let localStartedAt = Date.now();
	let activeStatusKey = '';
	let interval;

	onMount(() => {
		interval = setInterval(() => {
			now = Date.now();
		}, 1000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});

	const getStartedAtMs = (value) => {
		const parsed = Number(value);
		if (!Number.isFinite(parsed) || parsed <= 0) {
			return localStartedAt;
		}

		return parsed > 100000000000 ? parsed : parsed * 1000;
	};

	const formatElapsed = (seconds) => {
		const safeSeconds = Math.max(0, Math.floor(seconds));
		const minutes = Math.floor(safeSeconds / 60);
		const remainder = safeSeconds % 60;

		return `${minutes}:${remainder.toString().padStart(2, '0')}`;
	};

	$: isActive = status && (done || status?.done) === false;
	$: isWebSearchStatus =
		status?.action === 'web_search' || status?.action === 'web_search_queries_generated';
	$: statusKey = `${status?.action ?? ''}:${status?.description ?? ''}:${(status?.queries ?? []).join('|')}`;
	$: if (isActive && statusKey !== activeStatusKey) {
		activeStatusKey = statusKey;
		localStartedAt = Date.now();
	}
	$: elapsedSeconds = isActive ? (now - getStartedAtMs(status?.started_at)) / 1000 : 0;
	$: elapsedLabel = formatElapsed(elapsedSeconds);
</script>

{#if !status?.hidden}
	<div class="status-description flex items-center gap-2 py-0.5 w-full text-left">
		{#if status?.action === 'web_search' && (status?.urls || status?.items)}
			<WebSearchResults {status}>
				<div class="flex flex-col justify-center -space-y-0.5">
					<div
						class="{(done || status?.done) === false
							? 'shimmer'
							: ''} text-base line-clamp-1 text-wrap"
					>
						<!-- $i18n.t("Generating search query") -->
						<!-- $i18n.t("No search query generated") -->
						<!-- $i18n.t('Searched {{count}} sites') -->
						{#if status?.description?.includes('{{count}}')}
							{$i18n.t(status?.description, {
								count: (status?.urls || status?.items).length
							})}
						{:else if status?.description === 'No search query generated'}
							{$i18n.t('No search query generated')}
						{:else if status?.description === 'Generating search query'}
							{$i18n.t('Generating search query')}
						{:else}
							{status?.description}
						{/if}
					</div>
				</div>
			</WebSearchResults>
		{:else if status?.action === 'knowledge_search'}
			<div class="flex flex-col justify-center -space-y-0.5">
				<div
					class="{(done || status?.done) === false
						? 'shimmer'
						: ''} text-gray-500 dark:text-gray-500 text-base line-clamp-1 text-wrap"
				>
					{$i18n.t(`Searching Knowledge for "{{searchQuery}}"`, {
						searchQuery: status.query
					})}
				</div>
			</div>
		{:else if status?.action === 'web_search_queries_generated' && status?.queries}
			<div class="flex flex-col justify-center -space-y-0.5">
				<div class="flex items-center gap-2 text-gray-500 dark:text-gray-500 text-base line-clamp-1 text-wrap">
					{#if isActive}
						<span class="relative flex size-2 shrink-0">
							<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-gray-400 opacity-60"></span>
							<span class="relative inline-flex size-2 rounded-full bg-gray-500 dark:bg-gray-400"></span>
						</span>
					{/if}
					<span class="{isActive ? 'shimmer' : ''}">
						{$i18n.t(status?.description || 'Searching the web')}
					</span>
					{#if isActive}
						<span class="text-xs text-gray-400 dark:text-gray-600">{$i18n.t('for')} {elapsedLabel}</span>
					{/if}
				</div>

				<div class=" flex gap-1 flex-wrap mt-2">
					{#each status.queries as query, idx (query)}
						<div
							class="bg-gray-50 dark:bg-gray-850 flex rounded-lg py-1 px-2 items-center gap-1 text-xs"
						>
							<div>
								<Search className="size-3" />
							</div>

							<span class="line-clamp-1">
								{query}
							</span>
						</div>
					{/each}
				</div>
			</div>
		{:else if status?.action === 'queries_generated' && status?.queries}
			<div class="flex flex-col justify-center -space-y-0.5">
				<div
					class="{(done || status?.done) === false
						? 'shimmer'
						: ''} text-gray-500 dark:text-gray-500 text-base line-clamp-1 text-wrap"
				>
					{$i18n.t(`Querying`)}
				</div>

				<div class=" flex gap-1 flex-wrap mt-2">
					{#each status.queries as query, idx (query)}
						<div
							class="bg-gray-50 dark:bg-gray-850 flex rounded-lg py-1 px-2 items-center gap-1 text-xs"
						>
							<div>
								<Search className="size-3" />
							</div>

							<span class="line-clamp-1">
								{query}
							</span>
						</div>
					{/each}
				</div>
			</div>
		{:else if status?.action === 'sources_retrieved' && status?.count !== undefined}
			<div class="flex flex-col justify-center -space-y-0.5">
				<div
					class="{(done || status?.done) === false
						? 'shimmer'
						: ''} text-gray-500 dark:text-gray-500 text-base line-clamp-1 text-wrap"
				>
					{#if status.count === 0}
						{$i18n.t('No sources found')}
					{:else if status.count === 1}
						{$i18n.t('Retrieved 1 source')}
					{:else}
						<!-- {$i18n.t('Source')} -->
						<!-- {$i18n.t('No source available')} -->
						<!-- {$i18n.t('No distance available')} -->
						<!-- {$i18n.t('Retrieved {{count}} sources')} -->
						{$i18n.t('Retrieved {{count}} sources', {
							count: status.count
						})}
					{/if}
				</div>
			</div>
		{:else}
			<div class="flex flex-col justify-center -space-y-0.5">
				<div class="flex items-center gap-2 text-gray-500 dark:text-gray-500 text-base line-clamp-1 text-wrap">
					{#if isActive && isWebSearchStatus}
						<span class="relative flex size-2 shrink-0">
							<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-gray-400 opacity-60"></span>
							<span class="relative inline-flex size-2 rounded-full bg-gray-500 dark:bg-gray-400"></span>
						</span>
					{/if}
					<span class="{(done || status?.done) === false ? 'shimmer' : ''}">
						<!-- $i18n.t(`Searching "{{searchQuery}}"`) -->
						{#if status?.description?.includes('{{searchQuery}}')}
							{$i18n.t(status?.description, {
								searchQuery: status?.query
							})}
						{:else if status?.description === 'No search query generated'}
							{$i18n.t('No search query generated')}
						{:else if status?.description === 'Generating search query'}
							{$i18n.t('Generating search query')}
						{:else if status?.description === 'Searching the web'}
							{$i18n.t('Searching the web')}
						{:else}
							{status?.description}
						{/if}
					</span>
					{#if isActive && isWebSearchStatus}
						<span class="text-xs text-gray-400 dark:text-gray-600">{$i18n.t('for')} {elapsedLabel}</span>
					{/if}
				</div>

				{#if isActive && isWebSearchStatus && elapsedSeconds >= 12}
					<div class="mt-1 text-xs text-gray-400 dark:text-gray-600">
						{$i18n.t('Still waiting on the search provider...')}
					</div>
				{/if}
			</div>
		{/if}
	</div>
{/if}
