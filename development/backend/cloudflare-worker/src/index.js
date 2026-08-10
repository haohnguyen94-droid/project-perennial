export default {
	async fetch(request) {
		if (request.method !== 'POST') {
			return Response.json({ error: 'POST required' }, { status: 405 });
		}

		let body;

		try {
			body = await request.json();
		} catch {
			return Response.json({ error: 'Invalid request body' }, { status: 400 });
		}

		const targetUrl = body.url;
		const headers = body.headers ?? {};

		if (!targetUrl) {
			return Response.json({ error: 'Missing URL' }, { status: 400 });
		}

		let parsed;

		try {
			parsed = new URL(targetUrl);
		} catch {
			return Response.json({ error: 'Invalid URL' }, { status: 400 });
		}

		if (parsed.protocol !== 'https:') {
			return Response.json({ error: 'Only HTTPS is allowed' }, { status: 400 });
		}

		try {
			const upstream = await fetch(targetUrl, {
				method: 'GET',
				headers: headers,
			});

			if (!upstream.ok) {
				const preview = await upstream.text();

				return Response.json(
					{
						upstream_status: upstream.status,
						upstream_preview: preview.slice(0, 500),
					},
					{ status: upstream.status },
				);
			}

			return new Response(upstream.body, {
				status: upstream.status,
				headers: {
					'Content-Type': upstream.headers.get('Content-Type') ?? 'application/octet-stream',
				},
			});
		} catch (error) {
			return Response.json(
				{
					error: 'Upstream request failed',
					message: String(error),
				},
				{ status: 502 },
			);
		}
	},
};
