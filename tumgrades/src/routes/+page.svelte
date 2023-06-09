<script lang="ts">
	export let data;
</script>

<h1>Welcome to TUM-ECTS</h1>
<p>This is work in progress :(</p>
<ul>
	{#each data.degrees as degree}
		<li>{degree}</li>
	{/each}
</ul>
