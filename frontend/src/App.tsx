import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { detectFaces, autoMask, swapFace, type FaceBox } from './api'
import { MaskEditor } from './components/MaskEditor'

function useObjectUrl(file: File | null) {
	const [url, setUrl] = useState<string | null>(null)
	useEffect(() => {
		if (!file) { setUrl(null); return }
		const u = URL.createObjectURL(file)
		setUrl(u)
		return () => URL.revokeObjectURL(u)
	}, [file])
	return url
}

function App() {
	const [baseFile, setBaseFile] = useState<File | null>(null)
	const [replacementFile, setReplacementFile] = useState<File | null>(null)
	const [maskFile, setMaskFile] = useState<File | null>(null)
	const [faces, setFaces] = useState<FaceBox[]>([])
	const [selectedFace, setSelectedFace] = useState<FaceBox | null>(null)
	const [resultBlob, setResultBlob] = useState<Blob | null>(null)
	const [loading, setLoading] = useState<string | null>(null)
	const baseUrl = useObjectUrl(baseFile)
	const replUrl = useObjectUrl(replacementFile)
	const resultUrl = useMemo(() => (resultBlob ? URL.createObjectURL(resultBlob) : null), [resultBlob])
	useEffect(() => () => { if (resultUrl) URL.revokeObjectURL(resultUrl) }, [resultUrl])

	async function onDetect() {
		if (!baseFile) return
		setLoading('Detecting faces...')
		try {
			const f = await detectFaces(baseFile)
			setFaces(f)
			setSelectedFace(f[0] ?? null)
		} finally { setLoading(null) }
	}

	async function onAutoMask() {
		if (!baseFile || !selectedFace) return
		setLoading('Generating mask...')
		try {
			const blob = await autoMask(baseFile, selectedFace, 18)
			setMaskFile(new File([blob], 'mask.png', { type: 'image/png' }))
		} finally { setLoading(null) }
	}

	async function onSwap() {
		if (!baseFile || !replacementFile || !selectedFace) return
		setLoading('Swapping face...')
		try {
			const blob = await swapFace(baseFile, replacementFile, maskFile, selectedFace, 'mixed')
			setResultBlob(blob)
		} finally { setLoading(null) }
	}

	return (
		<div className="container">
			<h2>Watercolor Face Swap</h2>
			{loading && <p>{loading}</p>}
			<div className="row">
				<div className="panel" style={{ flex: '1 1 320px' }}>
					<h3>1) Upload illustration</h3>
					<input type="file" accept="image/*" onChange={(e) => setBaseFile(e.target.files?.[0] ?? null)} />
					{baseUrl && <img src={baseUrl} style={{ maxWidth: '100%', marginTop: 8 }} />}
					<div className="controls">
						<button onClick={onDetect} disabled={!baseFile}>Auto-detect faces</button>
					</div>
					{faces.length > 0 && (
						<div>
							<p>Choose a face:</p>
							<div className="faces">
								{faces.map((b, idx) => (
									<button key={idx} className={"face" + (selectedFace === b ? ' selected' : '')} onClick={() => setSelectedFace(b)}>
										Box {idx+1}: {b.w}x{b.h}
									</button>
								))}
							</div>
						</div>
					)}
					<div className="controls">
						<button onClick={onAutoMask} disabled={!baseFile || !selectedFace}>Auto-generate mask</button>
					</div>
					{baseUrl && selectedFace && (
						<div>
							<h4>Mask editor</h4>
							<MaskEditor imageUrl={baseUrl} initialMaskUrl={maskFile ? URL.createObjectURL(maskFile) : undefined} onMaskChange={setMaskFile} />
						</div>
					)}
				</div>

				<div className="panel" style={{ flex: '1 1 320px' }}>
					<h3>2) Upload replacement face</h3>
					<input type="file" accept="image/*" onChange={(e) => setReplacementFile(e.target.files?.[0] ?? null)} />
					{replUrl && <img src={replUrl} style={{ maxWidth: '100%', marginTop: 8 }} />}
					<div className="controls">
						<button onClick={onSwap} disabled={!baseFile || !replacementFile || !selectedFace}>Swap</button>
					</div>
				</div>

				<div className="panel" style={{ flex: '1 1 320px' }}>
					<h3>3) Result</h3>
					{resultUrl ? (
						<div>
							<img src={resultUrl} style={{ maxWidth: '100%', marginTop: 8 }} />
							<div className="controls">
								<a href={resultUrl} download="result.png">
									<button>Download</button>
								</a>
							</div>
						</div>
					) : (
						<p>No result yet.</p>
					)}
				</div>
			</div>
		</div>
	)
}

export default App
