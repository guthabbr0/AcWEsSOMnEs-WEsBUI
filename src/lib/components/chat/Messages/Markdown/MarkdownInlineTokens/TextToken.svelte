<script lang="ts">
	import { fade } from 'svelte/transition';
	import { config, shortCodesToEmojis } from '$lib/stores';
	import { WEBUI_BASE_URL } from '$lib/constants';

	export let token;
	export let done = true;

	let texts = [];
	$: texts = (token?.raw ?? '').split(' ');

	type TextPart =
		| {
				type: 'text';
				value: string;
		  }
		| {
				type: 'emoji';
				src: string;
				alt: string;
				title: string;
		  };

	const normalizeShortCode = (value: string) =>
		String(value ?? '')
			.trim()
			.replace(/^:+|:+$/g, '')
			.toLowerCase();

	const normalizeCodepoint = (value: unknown) =>
		String(value ?? '')
			.trim()
			.toLowerCase();

	const unicodeToCodepoint = (value: string) =>
		Array.from(value)
			.map((char) => char.codePointAt(0)?.toString(16).toLowerCase().padStart(4, '0'))
			.filter((part): part is string => Boolean(part))
			.join('-');

	const codepointToEmojiSrc = (codepoint: string) =>
		`${WEBUI_BASE_URL}/assets/emojis/${normalizeCodepoint(codepoint)}.svg`;

	const getCustomEmojiDataUrl = (shortCode: string, customShortCodes: Map<string, string>) =>
		customShortCodes.get(shortCode) ?? null;

	const resolveUnicodeCodepoint = (unicodeEmoji: string, standardCodepoints: Set<string>) => {
		const exact = unicodeToCodepoint(unicodeEmoji);
		if (exact && standardCodepoints.has(exact)) {
			return exact;
		}

		const withoutTextVariation = exact.replace(/-fe0e/g, '');
		if (withoutTextVariation && standardCodepoints.has(withoutTextVariation)) {
			return withoutTextVariation;
		}

		const withoutEmojiVariation = exact.replace(/-fe0f/g, '');
		if (withoutEmojiVariation && standardCodepoints.has(withoutEmojiVariation)) {
			return withoutEmojiVariation;
		}

		return null;
	};

	const emojiTokenRegex =
		/:([a-zA-Z0-9_+\-]+):|(?:\p{Regional_Indicator}{2}|[0-9#*]\uFE0F?\u20E3|(?:\p{Extended_Pictographic}|\p{Emoji_Presentation}|\p{Emoji}\uFE0F)(?:[\uFE0E\uFE0F]|\p{Emoji_Modifier})*(?:\u200D(?:\p{Extended_Pictographic}|\p{Emoji_Presentation}|\p{Emoji}\uFE0F)(?:[\uFE0E\uFE0F]|\p{Emoji_Modifier})*)*)/gu;

	let textParts: TextPart[] = [];

	$: {
		const raw = String(token?.raw ?? '');
		const parts: TextPart[] = [];
		const standardCodepoints = new Set<string>();
		const customShortCodes = new Map<string, string>();

		for (const customEmoji of Array.isArray($config?.ui?.custom_emojis)
			? $config.ui.custom_emojis
			: []) {
			const shortCode = normalizeShortCode(customEmoji?.name ?? '');
			const dataUrl = String(customEmoji?.data_url ?? '').trim();
			if (shortCode && dataUrl.startsWith('data:image/')) {
				customShortCodes.set(shortCode, dataUrl);
			}
		}

		for (const codepoint of Object.values($shortCodesToEmojis ?? {})) {
			const normalizedCodepoint = normalizeCodepoint(codepoint);
			if (normalizedCodepoint) {
				standardCodepoints.add(normalizedCodepoint);
			}
		}

		let cursor = 0;
		emojiTokenRegex.lastIndex = 0;

		for (const match of raw.matchAll(emojiTokenRegex)) {
			const matchedValue = match[0] ?? '';
			const matchIndex = match.index ?? 0;

			if (matchIndex > cursor) {
				parts.push({
					type: 'text',
					value: raw.slice(cursor, matchIndex)
				});
			}

			const shortCodeMatch = match[1] ? normalizeShortCode(match[1]) : '';
			const customEmojiDataUrl = shortCodeMatch
				? getCustomEmojiDataUrl(shortCodeMatch, customShortCodes)
				: null;
			const standardEmojiCodepoint = normalizeCodepoint(
				shortCodeMatch ? $shortCodesToEmojis[shortCodeMatch] : ''
			);
			const unicodeEmojiCodepoint = shortCodeMatch
				? null
				: resolveUnicodeCodepoint(matchedValue, standardCodepoints);

			if (customEmojiDataUrl || standardEmojiCodepoint || unicodeEmojiCodepoint) {
				const title = shortCodeMatch ? `:${shortCodeMatch}:` : matchedValue;
				parts.push({
					type: 'emoji',
					src:
						customEmojiDataUrl ??
						codepointToEmojiSrc(standardEmojiCodepoint || unicodeEmojiCodepoint || ''),
					alt: title,
					title
				});
			} else {
				parts.push({
					type: 'text',
					value: matchedValue
				});
			}

			cursor = matchIndex + matchedValue.length;
		}

		if (cursor < raw.length) {
			parts.push({
				type: 'text',
				value: raw.slice(cursor)
			});
		}

		textParts = parts;
	}
</script>

{#if done}
	{#each textParts as part}
		{#if part.type === 'emoji'}
			<img
				src={part.src}
				alt={part.alt}
				title={part.title}
				class="inline-block h-[1.12em] w-[1.12em] object-contain align-[-0.16em]"
				loading="lazy"
				draggable="false"
			/>
		{:else}
			{part.value}
		{/if}
	{/each}
{:else}
	{#each (token?.raw ?? '').split(' ') as text}
		<span class="fade-in-token">
			{text}{' '}
		</span>
	{/each}
{/if}
