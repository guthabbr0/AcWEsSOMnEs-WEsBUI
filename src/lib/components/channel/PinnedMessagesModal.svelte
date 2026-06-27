<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext, onMount } from 'svelte';
	const i18n = getContext('i18n');

	import { getChannelPinnedMessages, pinMessage } from '$lib/apis/channels';

	import Spinner from '$lib/components/common/Spinner.svelte';

	import XMark from '$lib/components/icons/XMark.svelte';
	import Message from './Messages/Message.svelte';
	import Loader from '../common/Loader.svelte';

	export let show = false;
	export let channel = null;
	export let onPin = (messageId, pinned) => {};

	let page = 1;
	let pinnedMessages = null;

	let allItemsLoaded = false;
	let loading = false;
	let wasOpen = false;

	const getPinnedMessages = async () => {
		if (!channel) return;
		if (allItemsLoaded) return;

		loading = true;
		try {
			const res = await getChannelPinnedMessages(localStorage.token, channel.id, page).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				pinnedMessages = [...(pinnedMessages ?? []), ...res];

				if (res.length === 0) {
					allItemsLoaded = true;
				}
			}
		} catch (error) {
			console.error('Error fetching pinned messages:', error);
		} finally {
			loading = false;
		}
	};

	const init = () => {
		page = 1;
		pinnedMessages = null;
		allItemsLoaded = false;

		getPinnedMessages();
	};

	$: if (show && !wasOpen) {
		init();
	}

	$: wasOpen = show;

	onMount(() => {
		init();
	});
</script>

{#if channel && show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		class="fixed inset-0 z-50 flex justify-end bg-black/30"
		on:click={() => {
			show = false;
		}}
	>
		<div
			class="h-full w-full max-w-md border-l border-gray-100 bg-white shadow-xl dark:border-gray-850 dark:bg-gray-900"
			on:click|stopPropagation
		>
			<div class="flex h-full flex-col">
				<div
					class="flex items-center justify-between border-b border-gray-100 px-5 py-4 dark:border-gray-850 dark:text-gray-100"
				>
					<div class="self-center text-base font-medium">
						{$i18n.t('Pinned Messages')}
				</div>
					<button
						class="self-center rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-850 dark:hover:text-gray-300"
						on:click={() => {
							show = false;
						}}
					>
						<XMark className={'size-5'} />
					</button>
				</div>

				<div class="flex min-h-0 flex-1 flex-col px-4 pb-4 dark:text-gray-200">
					{#if pinnedMessages === null}
						<div class="my-10">
							<Spinner className="size-5" />
						</div>
					{:else}
						<div
							class="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700 scrollbar-track-transparent py-2"
						>
							{#if pinnedMessages.length === 0}
								<div class=" text-center text-xs text-gray-500 dark:text-gray-400 py-6">
									{$i18n.t('No pinned messages')}
								</div>
							{:else}
								{#each pinnedMessages as message, messageIdx (message.id)}
									<Message
										className="rounded-xl px-2"
										{message}
										{channel}
										onPin={async (message) => {
											pinnedMessages = pinnedMessages.filter((m) => m.id !== message.id);
											onPin(message.id, !message.is_pinned);

											const updatedMessage = await pinMessage(
												localStorage.token,
												message.channel_id,
												message.id,
												!message.is_pinned
											).catch((error) => {
												toast.error(`${error}`);
												return null;
											});

											init();
										}}
										onReaction={false}
										onThread={false}
										onReply={false}
										onEdit={false}
										onDelete={false}
									/>

									{#if messageIdx === pinnedMessages.length - 1 && !allItemsLoaded}
										<Loader
											on:visible={(e) => {
												console.log('visible');
												if (!loading) {
													page += 1;
													getPinnedMessages();
												}
											}}
										>
											<div
												class="w-full flex justify-center py-1 text-xs animate-pulse items-center gap-2"
											>
												<Spinner className=" size-4" />
												<div class=" ">{$i18n.t('Loading...')}</div>
											</div>
										</Loader>
									{/if}
								{/each}
							{/if}
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
