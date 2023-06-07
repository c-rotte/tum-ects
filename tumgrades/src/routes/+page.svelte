<script lang="ts">
	import type { PageData } from './$types';
	export let data: PageData;
</script>

<h1>Welcome to TUM-ECTS</h1>
<p>Here are our GraphQL schemas:</p>
<pre>{data.gqlTypeDefs}</pre>
