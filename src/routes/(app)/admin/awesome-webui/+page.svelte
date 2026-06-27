<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		goto('/admin/awesome-webui/authorization', { replaceState: true });
	});
</script>
