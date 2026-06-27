<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import localizedFormat from 'dayjs/plugin/localizedFormat';

	import {
		getModerationCenter,
		resolveModerationAppeal,
		revokeModerationBan
	} from '$lib/apis/moderation';

	import Spinner from '$lib/components/common/Spinner.svelte';

	dayjs.extend(localizedFormat);

	const i18n = getContext('i18n');

	let loading = true;
	let center: any = null;

	const formatDate = (timestamp: number | null | undefined) => {
		if (!timestamp) {
			return $i18n.t('Never');
		}
		return dayjs.unix(timestamp).format('lll');
	};

	const riskClass = (level: string) => {
		if (level === 'high') return 'bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-300';
		if (level === 'medium') return 'bg-yellow-50 text-yellow-700 dark:bg-yellow-950/30 dark:text-yellow-300';
		if (level === 'low') return 'bg-blue-50 text-blue-700 dark:bg-blue-950/30 dark:text-blue-300';
		return 'bg-gray-50 text-gray-600 dark:bg-gray-850 dark:text-gray-300';
	};

	const loadCenter = async () => {
		loading = true;
		const res = await getModerationCenter(localStorage.token, 150).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (res) {
			center = res;
		}
		loading = false;
	};

	const resolveAppealHandler = async (appealId: string, status: string) => {
		const res = await resolveModerationAppeal(localStorage.token, appealId, status).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (res) {
			toast.success(status === 'resolved' ? $i18n.t('Appeal resolved') : $i18n.t('Appeal rejected'));
			await loadCenter();
		}
	};

	const revokeBanHandler = async (banId: string) => {
		const res = await revokeModerationBan(localStorage.token, banId).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (res) {
			toast.success($i18n.t('Ban revoked'));
			await loadCenter();
		}
	};

	$: pendingAppeals = center?.appeals ?? [];
	$: activeBans = (center?.bans ?? []).filter((ban: any) => !ban.revoked_at && (!ban.expires_at || ban.expires_at > Math.floor(Date.now() / 1000)));
	$: risks = center?.risks ?? [];
	$: audit = center?.audit ?? [];

	onMount(loadCenter);
</script>

<div class="flex h-full flex-col gap-4 px-4 py-2 text-sm">
	<div class="flex flex-wrap items-center justify-between gap-3">
		<div>
			<div class="text-lg font-medium">{$i18n.t('Moderation')}</div>
			<div class="text-xs text-gray-500 dark:text-gray-400">
				{$i18n.t('Appeals, bans, risk signals, and admin moderation activity.')}
			</div>
		</div>

		<button
			class="rounded-full bg-black px-3 py-1.5 text-xs font-medium text-white transition hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100"
			type="button"
			on:click={loadCenter}
		>
			{$i18n.t('Refresh')}
		</button>
	</div>

	{#if loading}
		<div class="flex flex-1 items-center justify-center">
			<Spinner className="size-5" />
		</div>
	{:else if center}
		<div class="grid gap-3 md:grid-cols-4">
			<div class="rounded-xl border border-gray-100 p-3 dark:border-gray-850">
				<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Pending appeals')}</div>
				<div class="mt-1 text-2xl font-medium">{pendingAppeals.length}</div>
			</div>
			<div class="rounded-xl border border-gray-100 p-3 dark:border-gray-850">
				<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Active bans')}</div>
				<div class="mt-1 text-2xl font-medium">{activeBans.length}</div>
			</div>
			<div class="rounded-xl border border-gray-100 p-3 dark:border-gray-850">
				<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Tracked users')}</div>
				<div class="mt-1 text-2xl font-medium">{risks.length}</div>
			</div>
			<div class="rounded-xl border border-gray-100 p-3 dark:border-gray-850">
				<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Audit events')}</div>
				<div class="mt-1 text-2xl font-medium">{audit.length}</div>
			</div>
		</div>

		<div class="grid min-h-0 gap-4 xl:grid-cols-[1.15fr_0.85fr]">
			<section class="space-y-2">
				<div class="text-sm font-medium">{$i18n.t('Appeals')}</div>
				<div class="divide-y divide-gray-100 rounded-xl border border-gray-100 dark:divide-gray-850 dark:border-gray-850">
					{#if pendingAppeals.length === 0}
						<div class="p-3 text-xs text-gray-500 dark:text-gray-400">{$i18n.t('No pending appeals.')}</div>
					{:else}
						{#each pendingAppeals as appeal}
							<div class="space-y-2 p-3">
								<div class="flex flex-wrap items-center justify-between gap-2">
									<div class="min-w-0">
										<div class="truncate font-medium">{appeal.user_id}</div>
										<div class="text-xs text-gray-500 dark:text-gray-400">{formatDate(appeal.created_at)}</div>
									</div>
									<div class="flex gap-2">
										<button class="rounded-lg border border-gray-100 px-2 py-1 text-xs hover:bg-gray-50 dark:border-gray-850 dark:hover:bg-gray-850" type="button" on:click={() => resolveAppealHandler(appeal.id, 'rejected')}>
											{$i18n.t('Reject')}
										</button>
										<button class="rounded-lg bg-black px-2 py-1 text-xs text-white hover:bg-gray-900 dark:bg-white dark:text-black dark:hover:bg-gray-100" type="button" on:click={() => resolveAppealHandler(appeal.id, 'resolved')}>
											{$i18n.t('Resolve')}
										</button>
									</div>
								</div>
								<div class="whitespace-pre-wrap rounded-lg bg-gray-50 p-2 text-xs dark:bg-gray-850">{appeal.message}</div>
							</div>
						{/each}
					{/if}
				</div>
			</section>

			<section class="space-y-2">
				<div class="text-sm font-medium">{$i18n.t('User risk')}</div>
				<div class="divide-y divide-gray-100 rounded-xl border border-gray-100 dark:divide-gray-850 dark:border-gray-850">
					{#if risks.length === 0}
						<div class="p-3 text-xs text-gray-500 dark:text-gray-400">{$i18n.t('No risk signals yet.')}</div>
					{:else}
						{#each risks as risk}
							<div class="flex items-start justify-between gap-3 p-3">
								<div class="min-w-0">
									<div class="truncate font-medium">{risk.user_id}</div>
									<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										{risk.reasons?.join(' • ') || $i18n.t('No recent moderation signals')}
									</div>
								</div>
								<div class="shrink-0 rounded-full px-2 py-1 text-xs font-medium {riskClass(risk.level)}">
									{risk.score}
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</section>
		</div>

		<div class="grid min-h-0 gap-4 xl:grid-cols-[1.15fr_0.85fr]">
			<section class="space-y-2">
				<div class="text-sm font-medium">{$i18n.t('Active bans')}</div>
				<div class="divide-y divide-gray-100 rounded-xl border border-gray-100 dark:divide-gray-850 dark:border-gray-850">
					{#if activeBans.length === 0}
						<div class="p-3 text-xs text-gray-500 dark:text-gray-400">{$i18n.t('No active bans.')}</div>
					{:else}
						{#each activeBans as ban}
							<div class="flex items-start justify-between gap-3 p-3">
								<div class="min-w-0">
									<div class="truncate font-medium">{ban.user_id}</div>
									<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										{ban.scope} • {$i18n.t('Expires')} {formatDate(ban.expires_at)}
									</div>
									<div class="mt-1 whitespace-pre-wrap text-xs">{ban.reason}</div>
								</div>
								<button class="shrink-0 rounded-lg border border-gray-100 px-2 py-1 text-xs hover:bg-gray-50 dark:border-gray-850 dark:hover:bg-gray-850" type="button" on:click={() => revokeBanHandler(ban.id)}>
									{$i18n.t('Unban')}
								</button>
							</div>
						{/each}
					{/if}
				</div>
			</section>

			<section class="space-y-2">
				<div class="text-sm font-medium">{$i18n.t('Audit')}</div>
				<div class="max-h-96 overflow-y-auto rounded-xl border border-gray-100 dark:border-gray-850">
					{#if audit.length === 0}
						<div class="p-3 text-xs text-gray-500 dark:text-gray-400">{$i18n.t('No audit events.')}</div>
					{:else}
						{#each audit as entry}
							<div class="border-b border-gray-100 p-3 last:border-b-0 dark:border-gray-850">
								<div class="flex items-center justify-between gap-3">
									<div class="truncate font-medium">{entry.action}</div>
									<div class="shrink-0 text-xs text-gray-500 dark:text-gray-400">{formatDate(entry.created_at)}</div>
								</div>
								<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{entry.actor_user_id || $i18n.t('System')} -> {entry.target_user_id || $i18n.t('System')}
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</section>
		</div>
	{/if}
</div>
