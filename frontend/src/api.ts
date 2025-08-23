export type FaceBox = { x: number; y: number; w: number; h: number };

export async function detectFaces(file: File): Promise<FaceBox[]> {
	const form = new FormData();
	form.append('image', file);
	const res = await fetch('/api/detect-faces', { method: 'POST', body: form });
	if (!res.ok) throw new Error('Face detection failed');
	const data = await res.json();
	return data.faces ?? [];
}

export async function autoMask(file: File, box: FaceBox, featherPx = 12): Promise<Blob> {
	const form = new FormData();
	form.append('image', file);
	form.append('x', String(box.x));
	form.append('y', String(box.y));
	form.append('w', String(box.w));
	form.append('h', String(box.h));
	form.append('feather_px', String(featherPx));
	const res = await fetch('/api/auto-mask', { method: 'POST', body: form });
	if (!res.ok) throw new Error('Auto-mask failed');
	return await res.blob();
}

export async function swapFace(
	base: File,
	replacement: File,
	mask: File | null,
	box: FaceBox,
	cloneMode: 'mixed' | 'normal' = 'mixed',
): Promise<Blob> {
	const form = new FormData();
	form.append('base_image', base);
	form.append('replacement_image', replacement);
	if (mask) form.append('mask_image', mask);
	form.append('x', String(box.x));
	form.append('y', String(box.y));
	form.append('w', String(box.w));
	form.append('h', String(box.h));
	form.append('clone_mode', cloneMode);
	const res = await fetch('/api/swap-face', { method: 'POST', body: form });
	if (!res.ok) throw new Error('Swap failed');
	return await res.blob();
}