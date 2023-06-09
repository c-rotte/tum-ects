<script lang="ts">
	import type { Degree } from '@prisma/client';
	export function printDegree(degree: Degree) {
		return `${degree.number}-${degree.fullNameDE}: (${degree.subtitleDE})`;
	}
	export let data;
</script>

<h1>Welcome to TUM-ECTS</h1>
<p>This is work in progress :(</p>
<ul>
	{#each data.degrees as degree}
		<li>{printDegree(degree)}</li>
	{/each}
</ul>
