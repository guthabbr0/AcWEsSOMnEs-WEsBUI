<script lang="ts">
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import { getModels } from '$lib/apis';
	import { getChannels } from '$lib/apis/channels';
	import {
		createModerationBan,
		getModerationAppeals,
		getModerationAuditLogs,
		getModerationBans,
		getModerationUserRisk,
		resolveModerationAppeal,
		revokeModerationBan
	} from '$lib/apis/moderation';
	import Modal from '$lib/components/common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
	export let selectedUser;

	const banTypes = [
		{ id: 'site', label: 'Website' },
		{ id: 'models', label: 'Models' },
		{ id: 'channels', label: 'Channels' }
	];

	let scope = 'site';
	let reason = '';
	let durationMonths = 0;
	let durationDays = 0;
	let durationMinutes = 60;
	let channelTargetMode = 'all';
	let selectedModelIds: string[] = [];
	let selectedChannelIds: string[] = [];
	let models = [];
	let channels = [];
	let targetsLoading = false;
	let activeBans = [];
	let appeals = [];
	let auditLogs = [];
	let risk = null;
	let loading = false;
	let revokingBanId = null;
	let resolvingAppealId = null;
	let wasOpen = false;

	$: if (show && !wasOpen) {
		init();
	}

	$: wasOpen = show;

	const init = () => {
		scope = 'site';
		reason = '';
		durationMonths = 0;
		durationDays = 0;
		durationMinutes = 60;
		channelTargetMode = 'all';
		selectedModelIds = [];
		selectedChannelIds = [];
		loading = false;
		activeBans = [];
		appeals = [];
		auditLogs = [];
		risk = null;
		void loadTargets();
		void loadActiveBans();
		void loadAppeals();
		void loadAuditLogs();
		void loadRisk();
	};

	const getDurationSeconds = () => {
		const months = Math.max(0, Number(durationMonths || 0));
		const days = Math.max(0, Number(durationDays || 0));
		const minutes = Math.max(0, Number(durationMinutes || 0));
		return Math.max(60, Math.round((months * 30 * 24 * 60 + days * 24 * 60 + minutes) * 60));
	};

	const getTargetLabel = () => {
		if (scope === 'models') {
			return $i18n.t('Models');
		}
		return $i18n.t('Channels');
	};

	const getModelLabel = (model) => model?.name || model?.id || $i18n.t('Unnamed model');
	const getChannelLabel = (channel) => channel?.name || channel?.id || $i18n.t('Unnamed channel');
	const getChannelsForMode = () => {
		if (channelTargetMode === 'all') {
			return [];
		}

		return channels
			.filter((channel) =>
				channelTargetMode === 'dms'
					? channel.type === 'dm'
					: channel.type !== 'dm'
			)
			.map((channel) => channel.id);
	};

	const toggleSelection = (id: string, collection: 'models' | 'channels') => {
		if (!id) {
			return;
		}

		if (collection === 'models') {
			selectedModelIds = selectedModelIds.includes(id)
				? selectedModelIds.filter((item) => item !== id)
				: [...selectedModelIds, id];
			return;
		}

		selectedChannelIds = selectedChannelIds.includes(id)
			? selectedChannelIds.filter((item) => item !== id)
			: [...selectedChannelIds, id];
	};

	const loadTargets = async () => {
		if (targetsLoading || (models.length > 0 && channels.length > 0)) {
			return;
		}

		targetsLoading = true;
		const [modelResponse, channelResponse] = await Promise.all([
			getModels(localStorage.token).catch((error) => {
				console.error(error);
				return [];
			}),
			getChannels(localStorage.token).catch((error) => {
				console.error(error);
				return [];
			})
		]);

		models = Array.isArray(modelResponse) ? modelResponse : [];
		channels = Array.isArray(channelResponse) ? channelResponse : [];
		targetsLoading = false;
	};

	const loadActiveBans = async () => {
		if (!selectedUser?.id) {
			activeBans = [];
			return;
		}

		const res = await getModerationBans(localStorage.token, selectedUser.id, false).catch((error) => {
			console.error(error);
			return null;
		});

		activeBans = Array.isArray(res?.items) ? res.items : [];
	};

	const loadAppeals = async () => {
		if (!selectedUser?.id) {
			appeals = [];
			return;
		}

		const res = await getModerationAppeals(localStorage.token, selectedUser.id).catch((error) => {
			console.error(error);
			return null;
		});

		appeals = Array.isArray(res?.items) ? res.items : [];
	};

	const loadAuditLogs = async () => {
		if (!selectedUser?.id) {
			auditLogs = [];
			return;
		}

		const res = await getModerationAuditLogs(localStorage.token, selectedUser.id, 25).catch((error) => {
			console.error(error);
			return null;
		});

		auditLogs = Array.isArray(res?.items) ? res.items : [];
	};

	const loadRisk = async () => {
		if (!selectedUser?.id) {
			risk = null;
			return;
		}

		risk = await getModerationUserRisk(localStorage.token, selectedUser.id).catch((error) => {
			console.error(error);
			return null;
		});
	};

	const getRiskClasses = (level) => {
		if (level === 'high') return 'bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-300';
		if (level === 'medium') return 'bg-yellow-50 text-yellow-700 dark:bg-yellow-950/30 dark:text-yellow-300';
		if (level === 'low') return 'bg-blue-50 text-blue-700 dark:bg-blue-950/30 dark:text-blue-300';
		return 'bg-gray-50 text-gray-600 dark:bg-gray-850 dark:text-gray-300';
	};

	const revokeBanHandler = async (banId) => {
		if (!banId || revokingBanId) {
			return;
		}

		revokingBanId = banId;
		const res = await revokeModerationBan(localStorage.token, banId).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		revokingBanId = null;

		if (res) {
			toast.success($i18n.t('Ban revoked'));
			await loadActiveBans();
			await loadAuditLogs();
			await loadRisk();
			dispatch('save');
		}
	};

	const resolveAppealHandler = async (appealId, status = 'resolved') => {
		if (!appealId || resolvingAppealId) {
			return;
		}

		resolvingAppealId = appealId;
		const res = await resolveModerationAppeal(localStorage.token, appealId, status).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		resolvingAppealId = null;

		if (res) {
			toast.success(status === 'rejected' ? $i18n.t('Appeal rejected') : $i18n.t('Appeal resolved'));
			await loadAppeals();
			await loadAuditLogs();
			await loadRisk();
		}
	};

	const getBanScopeLabel = (ban) => {
		if (ban?.scope === 'site') return $i18n.t('Website');
		if (ban?.scope === 'models') return $i18n.t('Models');
		if (ban?.scope === 'channels') return $i18n.t('Channels');
		return $i18n.t('Restriction');
	};

	const getBanExpiryLabel = (ban) => {
		if (!ban?.expires_at) return $i18n.t('No automatic expiry');
		return new Date(Number(ban.expires_at) * 1000).toLocaleString();
	};

	const submitHandler = async () => {
		if (!selectedUser?.id || loading) return;

		const trimmedReason = reason.trim();
		if (!trimmedReason) {
			toast.error($i18n.t('Reason is required'));
			return;
		}

		loading = true;

		const payload: Record<string, unknown> = {
			user_id: selectedUser.id,
			scope,
			reason: trimmedReason,
			duration_seconds: getDurationSeconds()
		};

		if (scope === 'models') {
			payload.model_ids = selectedModelIds;
		}

		if (scope === 'channels') {
			payload.channel_ids = channelTargetMode === 'custom' ? selectedChannelIds : getChannelsForMode();
		}

		const res = await createModerationBan(localStorage.token, payload).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		loading = false;

		if (res) {
			toast.success($i18n.t('Moderation ban created'));
			await loadActiveBans();
			await loadAuditLogs();
			await loadRisk();
			dispatch('save');
			show = false;
		}
	};

	onMount(() => {
		void loadTargets();
		void loadActiveBans();
		void loadAppeals();
		void loadAuditLogs();
		void loadRisk();
	});
</script>

<Modal size="sm" bind:show>
	<div>
		<div class="flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<div class="text-lg font-medium self-center">{$i18n.t('Moderate User')}</div>
			<button
				class="self-center text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition"
				aria-label={$i18n.t('Close')}
				on:click={() => {
					show = false;
				}}
			>
				<XMark className="size-5" />
			</button>
		</div>

		<form
			class="flex flex-col w-full px-5 pt-3 pb-5 text-sm dark:text-gray-200"
			on:submit|preventDefault={submitHandler}
		>
			<div class="flex items-center gap-3 min-w-0 mb-4">
				<img
					src={selectedUser?.profile_image_url ?? '/user.png'}
					alt=""
					class="size-10 rounded-full object-cover bg-gray-100 dark:bg-gray-850"
				/>
				<div class="min-w-0">
					<div class="font-medium truncate">{selectedUser?.name}</div>
					<div class="text-xs text-gray-500 truncate">{selectedUser?.email}</div>
				</div>
			</div>

			{#if risk}
				<div class="mb-4 rounded-xl border border-gray-100 p-3 dark:border-gray-850">
					<div class="flex items-start justify-between gap-3">
						<div class="min-w-0">
							<div class="text-xs font-medium text-gray-500">{$i18n.t('User risk')}</div>
							<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
								{risk.reasons?.length
									? risk.reasons.join(' • ')
									: $i18n.t('No moderation signals yet')}
							</div>
						</div>
						<div class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium {getRiskClasses(risk.level)}">
							{risk.score}
						</div>
					</div>
				</div>
			{/if}

			{#if activeBans.length > 0}
				<div class="mb-4 rounded-xl border border-gray-100 dark:border-gray-850 p-2">
					<div class="px-1 pb-1.5 text-xs font-medium text-gray-500">
						{$i18n.t('Active bans')}
					</div>
					<div class="flex flex-col gap-1.5">
						{#each activeBans as ban (ban.id)}
							<div
								class="rounded-lg bg-gray-50 px-3 py-2 text-xs dark:bg-gray-850"
							>
								<div class="flex items-start justify-between gap-3">
									<div class="min-w-0">
										<div class="font-medium text-gray-900 dark:text-gray-100">
											{getBanScopeLabel(ban)}
										</div>
										<div class="mt-0.5 truncate text-gray-500 dark:text-gray-400">
											{ban.reason}
										</div>
										<div class="mt-1 text-[11px] text-gray-400 dark:text-gray-500">
											{$i18n.t('Expires')}: {getBanExpiryLabel(ban)}
										</div>
									</div>
									<button
										type="button"
										class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50 dark:text-red-400 dark:hover:bg-red-950/30"
										disabled={revokingBanId === ban.id}
										on:click={() => {
											void revokeBanHandler(ban.id);
										}}
									>
										{revokingBanId === ban.id ? $i18n.t('Revoking') : $i18n.t('Unban')}
									</button>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			{#if appeals.length > 0}
				<div class="mb-4 rounded-xl border border-gray-100 dark:border-gray-850 p-2">
					<div class="px-1 pb-1.5 text-xs font-medium text-gray-500">
						{$i18n.t('Appeals')}
					</div>
					<div class="flex max-h-44 flex-col gap-1.5 overflow-y-auto">
						{#each appeals as appeal (appeal.id)}
							<div class="rounded-lg bg-gray-50 px-3 py-2 text-xs dark:bg-gray-850">
								<div class="flex items-start justify-between gap-3">
									<div class="min-w-0">
										<div class="flex items-center gap-2">
											<div class="font-medium text-gray-900 dark:text-gray-100">
												{$i18n.t(appeal.status)}
											</div>
											<div class="text-[11px] text-gray-400">
												{new Date(Number(appeal.created_at) * 1000).toLocaleString()}
											</div>
										</div>
										<div class="mt-1 whitespace-pre-wrap text-gray-600 dark:text-gray-300">
											{appeal.message}
										</div>
									</div>
									{#if appeal.status === 'pending'}
										<div class="flex shrink-0 flex-col gap-1">
											<button
												type="button"
												class="rounded-full px-2.5 py-1 text-xs font-medium text-gray-700 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50 dark:text-gray-200 dark:hover:bg-gray-800"
												disabled={resolvingAppealId === appeal.id}
												on:click={() => {
													void resolveAppealHandler(appeal.id, 'resolved');
												}}
											>
												{$i18n.t('Resolve')}
											</button>
											<button
												type="button"
												class="rounded-full px-2.5 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50 dark:text-red-400 dark:hover:bg-red-950/30"
												disabled={resolvingAppealId === appeal.id}
												on:click={() => {
													void resolveAppealHandler(appeal.id, 'rejected');
												}}
											>
												{$i18n.t('Reject')}
											</button>
										</div>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			{#if auditLogs.length > 0}
				<div class="mb-4 rounded-xl border border-gray-100 dark:border-gray-850 p-2">
					<div class="px-1 pb-1.5 text-xs font-medium text-gray-500">
						{$i18n.t('Moderation audit')}
					</div>
					<div class="flex max-h-36 flex-col gap-1 overflow-y-auto">
						{#each auditLogs as log (log.id)}
							<div class="flex items-center justify-between gap-3 rounded-lg px-2 py-1.5 text-xs hover:bg-gray-50 dark:hover:bg-gray-850">
								<div class="min-w-0">
									<div class="truncate font-medium text-gray-800 dark:text-gray-100">
										{log.action}
									</div>
									<div class="truncate text-[11px] text-gray-400">
										{log.actor_user_id ? `${$i18n.t('Actor')}: ${log.actor_user_id}` : $i18n.t('System')}
									</div>
								</div>
								<div class="shrink-0 text-[11px] text-gray-400">
									{new Date(Number(log.created_at) * 1000).toLocaleString()}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<div class="flex flex-col w-full mb-4">
				<div class="mb-1.5 text-xs text-gray-500">{$i18n.t('Restriction')}</div>
				<div class="flex flex-wrap gap-1 rounded-full bg-gray-50 dark:bg-gray-850 p-1 w-fit">
					{#each banTypes as type}
						<button
							class="px-3 py-1.5 rounded-full text-xs font-medium transition {scope === type.id
								? 'bg-white dark:bg-gray-700 shadow-xs text-gray-900 dark:text-gray-100'
								: 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'}"
							type="button"
							on:click={() => {
								scope = type.id;
								void loadTargets();
							}}
						>
							{$i18n.t(type.label)}
						</button>
					{/each}
				</div>
			</div>

			{#if scope === 'models' || scope === 'channels'}
				<div class="flex flex-col w-full mb-4">
					<div class="mb-1 flex items-center justify-between gap-2">
						<div class="text-xs text-gray-500">{getTargetLabel()}</div>
						<div class="text-[11px] text-gray-400 dark:text-gray-500">
							{#if scope === 'models'}
								{selectedModelIds.length === 0
									? $i18n.t('All models')
									: `${selectedModelIds.length} ${$i18n.t('selected')}`}
							{:else}
								{channelTargetMode === 'all'
									? $i18n.t('Everything')
									: channelTargetMode === 'dms'
										? $i18n.t('DMs')
										: channelTargetMode === 'channels'
											? $i18n.t('Channels')
											: selectedChannelIds.length === 0
												? $i18n.t('No channels selected')
									: `${selectedChannelIds.length} ${$i18n.t('selected')}`}
							{/if}
						</div>
					</div>

					{#if scope === 'models'}
						<button
							type="button"
							class="mb-2 w-fit rounded-full px-2.5 py-1 text-xs transition {selectedModelIds.length === 0
								? 'bg-gray-900 text-white dark:bg-white dark:text-black'
								: 'bg-gray-50 text-gray-600 hover:bg-gray-100 dark:bg-gray-850 dark:text-gray-300 dark:hover:bg-gray-800'}"
							on:click={() => {
								selectedModelIds = [];
							}}
						>
							{$i18n.t('All models')}
						</button>
					{:else}
						<div class="mb-2 flex flex-wrap gap-1 rounded-full bg-gray-50 p-1 dark:bg-gray-850 w-fit">
							{#each [
								{ id: 'all', label: 'Everything' },
								{ id: 'dms', label: 'DMs' },
								{ id: 'channels', label: 'Channels' },
								{ id: 'custom', label: 'Pick channels' }
							] as mode}
								<button
									type="button"
									class="rounded-full px-2.5 py-1 text-xs font-medium transition {channelTargetMode ===
									mode.id
										? 'bg-white text-gray-900 shadow-xs dark:bg-gray-700 dark:text-gray-100'
										: 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'}"
									on:click={() => {
										channelTargetMode = mode.id;
									}}
								>
									{$i18n.t(mode.label)}
								</button>
							{/each}
						</div>
					{/if}

					<div
						class="max-h-44 overflow-y-auto rounded-xl border border-gray-100 dark:border-gray-850 p-1 {scope ===
							'channels' && channelTargetMode !== 'custom'
							? 'hidden'
							: ''}"
					>
						{#if targetsLoading}
							<div class="px-2.5 py-3 text-xs text-gray-500">{$i18n.t('Loading...')}</div>
						{:else if scope === 'models'}
							{#if models.length === 0}
								<div class="px-2.5 py-3 text-xs text-gray-500">
									{$i18n.t('No models available')}
								</div>
							{:else}
								{#each models as model (model.id)}
									<button
										type="button"
										class="w-full rounded-lg px-2.5 py-2 text-left transition {selectedModelIds.includes(
											model.id
										)
											? 'bg-gray-100 dark:bg-gray-800'
											: 'hover:bg-gray-50 dark:hover:bg-gray-850'}"
										on:click={() => toggleSelection(model.id, 'models')}
									>
										<div class="flex items-center gap-2">
											<div
												class="size-4 rounded border flex items-center justify-center shrink-0 {selectedModelIds.includes(
													model.id
												)
													? 'border-gray-900 bg-gray-900 text-white dark:border-white dark:bg-white dark:text-black'
													: 'border-gray-300 dark:border-gray-700'}"
											>
												{#if selectedModelIds.includes(model.id)}
													<span class="text-[10px] leading-none">✓</span>
												{/if}
											</div>
											<div class="min-w-0">
												<div class="text-sm truncate">{getModelLabel(model)}</div>
												<div class="text-[11px] text-gray-500 dark:text-gray-400 truncate">
													{model.id}
												</div>
											</div>
										</div>
									</button>
								{/each}
							{/if}
						{:else if channels.length === 0}
							<div class="px-2.5 py-3 text-xs text-gray-500">
								{$i18n.t('No channels available')}
							</div>
						{:else}
							{#each channels as channel (channel.id)}
								<button
									type="button"
									class="w-full rounded-lg px-2.5 py-2 text-left transition {selectedChannelIds.includes(
										channel.id
									)
										? 'bg-gray-100 dark:bg-gray-800'
										: 'hover:bg-gray-50 dark:hover:bg-gray-850'}"
									on:click={() => toggleSelection(channel.id, 'channels')}
								>
									<div class="flex items-center gap-2">
										<div
											class="size-4 rounded border flex items-center justify-center shrink-0 {selectedChannelIds.includes(
												channel.id
											)
												? 'border-gray-900 bg-gray-900 text-white dark:border-white dark:bg-white dark:text-black'
												: 'border-gray-300 dark:border-gray-700'}"
										>
											{#if selectedChannelIds.includes(channel.id)}
												<span class="text-[10px] leading-none">✓</span>
											{/if}
										</div>
										<div class="min-w-0">
											<div class="text-sm truncate">{getChannelLabel(channel)}</div>
											<div class="text-[11px] text-gray-500 dark:text-gray-400 truncate">
												{channel.type || $i18n.t('standard')} · {channel.id}
											</div>
										</div>
									</div>
								</button>
							{/each}
						{/if}
					</div>
				</div>

				<hr class="border-gray-100/30 dark:border-gray-850/30 mb-4 w-full" />
			{/if}

			<div class="flex flex-col w-full mb-4">
				<div class="mb-1 text-xs text-gray-500">{$i18n.t('Duration')}</div>
				<div class="grid grid-cols-3 gap-2">
					<label class="rounded-xl border border-gray-100 px-3 py-2 dark:border-gray-850">
						<span class="mb-1 block text-[11px] text-gray-500">{$i18n.t('Months')}</span>
					<input
							class="w-full text-sm bg-transparent outline-hidden"
						type="number"
							min="0"
							bind:value={durationMonths}
							aria-label={$i18n.t('Months')}
					/>
					</label>
					<label class="rounded-xl border border-gray-100 px-3 py-2 dark:border-gray-850">
						<span class="mb-1 block text-[11px] text-gray-500">{$i18n.t('Days')}</span>
						<input
							class="w-full text-sm bg-transparent outline-hidden"
							type="number"
							min="0"
							bind:value={durationDays}
							aria-label={$i18n.t('Days')}
						/>
					</label>
					<label class="rounded-xl border border-gray-100 px-3 py-2 dark:border-gray-850">
						<span class="mb-1 block text-[11px] text-gray-500">{$i18n.t('Minutes')}</span>
						<input
							class="w-full text-sm bg-transparent outline-hidden"
							type="number"
							min="0"
							bind:value={durationMinutes}
							aria-label={$i18n.t('Minutes')}
						/>
					</label>
				</div>
			</div>

			<hr class="border-gray-100/30 dark:border-gray-850/30 mb-4 w-full" />

			<div class="flex flex-col w-full">
				<div class="mb-1 text-xs text-gray-500">{$i18n.t('Reason')}</div>
				<textarea
					class="w-full min-h-24 text-sm bg-transparent outline-hidden resize-none"
					placeholder={$i18n.t('Reason shown to the user')}
					bind:value={reason}
					required
				></textarea>
			</div>

			<div class="flex justify-end gap-2 pt-5 text-sm font-medium">
				<button
					class="px-3.5 py-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-850 transition"
					type="button"
					on:click={() => {
						show = false;
					}}
				>
					{$i18n.t('Cancel')}
				</button>
				<button
					class="px-3.5 py-1.5 rounded-full bg-red-600 hover:bg-red-700 text-white transition disabled:cursor-not-allowed disabled:opacity-50"
					type="submit"
					disabled={loading}
				>
					{loading ? $i18n.t('Creating') : $i18n.t('Create ban')}
				</button>
			</div>
		</form>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	input[type='number'] {
		-moz-appearance: textfield;
	}
</style>
