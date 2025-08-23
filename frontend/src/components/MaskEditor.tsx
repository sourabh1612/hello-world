import { useEffect, useRef, useState } from 'react'

export type Tool = 'brush' | 'eraser'

export function MaskEditor({
	imageUrl,
	initialMaskUrl,
	onMaskChange,
	brushSize = 24,
}: {
	imageUrl: string
	initialMaskUrl?: string
	onMaskChange: (file: File) => void
	brushSize?: number
}) {
	const canvasRef = useRef<HTMLCanvasElement | null>(null)
	const [tool, setTool] = useState<Tool>('brush')
	const [isDrawing, setIsDrawing] = useState(false)
	const [imgEl, setImgEl] = useState<HTMLImageElement | null>(null)
	const [maskEl, setMaskEl] = useState<HTMLImageElement | null>(null)

	useEffect(() => {
		const img = new Image()
		img.crossOrigin = 'anonymous'
		img.onload = () => setImgEl(img)
		img.src = imageUrl
	}, [imageUrl])

	useEffect(() => {
		if (!initialMaskUrl) return
		const m = new Image()
		m.crossOrigin = 'anonymous'
		m.onload = () => setMaskEl(m)
		m.src = initialMaskUrl
	}, [initialMaskUrl])

	useEffect(() => {
		const cvs = canvasRef.current
		if (!cvs || !imgEl) return
		cvs.width = imgEl.width
		cvs.height = imgEl.height
		const ctx = cvs.getContext('2d')!
		ctx.clearRect(0, 0, cvs.width, cvs.height)
		if (maskEl) ctx.drawImage(maskEl, 0, 0, cvs.width, cvs.height)
	}, [imgEl, maskEl])

	function handlePointerDown(e: React.PointerEvent<HTMLCanvasElement>) {
		setIsDrawing(true)
		draw(e)
	}
	function handlePointerMove(e: React.PointerEvent<HTMLCanvasElement>) {
		if (!isDrawing) return
		draw(e)
	}
	function handlePointerUp() {
		setIsDrawing(false)
		exportMask()
	}

	function draw(e: React.PointerEvent<HTMLCanvasElement>) {
		const cvs = canvasRef.current
		if (!cvs) return
		const rect = cvs.getBoundingClientRect()
		const x = ((e.clientX - rect.left) / rect.width) * cvs.width
		const y = ((e.clientY - rect.top) / rect.height) * cvs.height
		const ctx = cvs.getContext('2d')!
		ctx.save()
		ctx.globalCompositeOperation = tool === 'eraser' ? 'destination-out' : 'source-over'
		ctx.fillStyle = '#ffffff'
		ctx.beginPath()
		ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2)
		ctx.fill()
		ctx.restore()
	}

	function exportMask() {
		const cvs = canvasRef.current
		if (!cvs) return
		cvs.toBlob((blob) => {
			if (!blob) return
			onMaskChange(new File([blob], 'mask.png', { type: 'image/png' }))
		}, 'image/png')
	}

	return (
		<div style={{ position: 'relative', display: 'inline-block' }}>
			{imgEl && (
				<img src={imageUrl} style={{ display: 'block', width: imgEl.width, height: imgEl.height }} />
			)}
			<canvas
				ref={canvasRef}
				style={{ position: 'absolute', left: 0, top: 0, cursor: tool === 'eraser' ? 'crosshair' : 'pointer' }}
				onPointerDown={handlePointerDown}
				onPointerMove={handlePointerMove}
				onPointerUp={handlePointerUp}
				onPointerLeave={handlePointerUp}
			/>
			<div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
				<button onClick={() => setTool('brush')} disabled={tool === 'brush'}>Brush</button>
				<button onClick={() => setTool('eraser')} disabled={tool === 'eraser'}>Eraser</button>
			</div>
		</div>
	)
}