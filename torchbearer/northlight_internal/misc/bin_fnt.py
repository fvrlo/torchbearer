from __future__ import annotations

import ctypes
from io import BytesIO
from enum import IntEnum
from struct import pack, unpack, Struct
from typing import BinaryIO
from pathlib import Path
from dataclasses import dataclass, field

from PIL import Image

from torchbearer.mulch import Stream, OLen

# This is a refactor of NorthlightTools' binfnt implementation combined with eprilx/NorthlightFontMaker and AWTools functions.


@dataclass
class Glyph:
	vertexOffset: int
	vertexCount: int
	indexOffset: int
	indexCount: int
	glyphWidth: float
	unknown: OLen.bytes(36)
	
	def __init__(self, stream: Stream):     # width: 44 bytes
		with stream(size=2):
			self.vertexOffset = int(stream)
			self.vertexCount = int(stream)
			self.indexOffset = int(stream)
			self.indexCount = int(stream)
			self.unknown = stream[36]
			self.glyphWidth = 0.0


@dataclass
class Vertex:
	x: float
	y: float
	s: float
	t: float
	
	__struct__ = Struct("4f")
	
	@classmethod
	def read(cls, stream: Stream):
		return cls(*cls.__struct__.unpack(stream[16]))


@dataclass
class BinFont:
	version: int
	textureSize: int
	skipped: OLen.bytes(8)
	ddsStream: bytes
	
	numVertices: int
	numIndices: int
	numGlyphs: int
	numKernels: int
	
	verticies: dict[int, Vertex]
	indices: dict[int, float]
	glyphs: list[Glyph]
	kernels: dict[int, Kernel]
	
	def __init__(self, stream: Stream):
		self.version = int(stream)
		
		self.numVertices = int(stream)
		self.verticies = {i: Vertex.read(stream) for i in range(self.numVertices)}
		
		self.numIndices = int(stream)
		self.indices = {i: stream.f2 for i in range(self.numIndices)}
		
		self.numGlyphs = int(stream)
		self.glyphs = [Glyph(stream) for _ in range(self.numGlyphs)]
		
		for _ in range(65536):
			code = stream.i2 + 32
			if self.glyphs[code] != self.glyphs[-1]:
				continue
			self.glyphs[code] = self.glyphs[0]
			self.glyphs.pop()
		
		self.numKernels = int(stream)
		if self.version == 3:
			self.kernels = {i: Kernel.read_12(stream) for i in range(self.numKernels)}
			self.textureSize = int(stream)
			self.skipped = b'\x00\x00\x00\x00\x00\x00\x00\x00'
			self.ddsStream = stream[self.textureSize]
		elif self.version == 7:
			self.kernels = {i: Kernel.read_8(stream) for i in range(self.numKernels)}
			self.textureSize = 0
			self.skipped = stream[8]
			self.ddsStream = stream.read()


class FontVersionEnum(IntEnum):
	AW1 = 3
	AWR = 4
	QBR = 7




class CharDesc(ctypes.Structure):
	_fields_ = [
		("b_x1_1", ctypes.c_float), ("b_y2_1", ctypes.c_float), ("x_lo_1", ctypes.c_float), ("y_hi_1", ctypes.c_float),
		("b_x2_1", ctypes.c_float), ("b_y2_2", ctypes.c_float), ("x_hi_1", ctypes.c_float), ("y_hi_2", ctypes.c_float),
		("b_x2_2", ctypes.c_float), ("b_y1_1", ctypes.c_float), ("x_hi_2", ctypes.c_float), ("y_lo_1", ctypes.c_float),
		("b_x1_2", ctypes.c_float), ("b_y1_2", ctypes.c_float), ("x_lo_2", ctypes.c_float), ("y_lo_2", ctypes.c_float),
	]
	b_x1_1: float; b_y2_1: float; x_lo_1: float; y_hi_1: float; b_x2_1: float; b_y2_2: float; x_hi_1: float; y_hi_2: float
	b_x2_2: float; b_y1_1: float; x_hi_2: float; y_lo_1: float; b_x1_2: float; b_y1_2: float; x_lo_2: float; y_lo_2: float


class UnknDesc(ctypes.Structure):
	_fields_ = [(f"n{x}", ctypes.c_uint16) for x in range(1,7)]
	n1: int; n2: int; n3: int; n4: int; n5: int; n6: int


class AdvcDesc(ctypes.Structure):
	_fields_ = [
		("plus4", ctypes.c_uint16), ("num4", ctypes.c_uint16), ("plus6", ctypes.c_uint16), ("num6", ctypes.c_uint16), ("chnl", ctypes.c_uint32),
		("x1_1", ctypes.c_float), ("x1_2", ctypes.c_float), ("x2_1", ctypes.c_float), ("x2_2", ctypes.c_float),
		("y1_1", ctypes.c_float), ("y1_2", ctypes.c_float), ("y2_1", ctypes.c_float), ("y2_2", ctypes.c_float),
	]
	
	plus4: int
	num4: int
	plus6: int
	num6: int
	chnl: int
	x1_1: float; x1_2: float; x2_1: float; x2_2: float; y1_1: float; y1_2: float; y2_1: float; y2_2: float



@dataclass
class Kernel:
	a: int
	b: int
	val: float
	
	__struct_8__ = Struct("2Hf")
	__struct_12__ = Struct("2If")
	
	@classmethod
	def read_8(cls, stream: Stream) -> Kernel:
		return cls(*cls.__struct_8__.unpack(stream[8]))
	
	@classmethod
	def read_12(cls, stream: Stream) -> Kernel:
		return cls(*cls.__struct_12__.unpack(stream[12]))
	
	def pack(self) -> OLen.bytes(8):
		return self.__struct_8__.pack(self.a, self.b, self.val)

@dataclass
class Advance:
	plus4: int
	num4: int
	plus6: int
	num6: int
	chnl: int
	
	x1_1: float
	x1_2: float
	x2_1: float
	x2_2: float
	y1_1: float
	y1_2: float
	y2_1: float
	y2_2: float
	
	__struct__ = Struct("4HI8f")
	
	@classmethod
	def from_single(cls, plus4: int, num4: int, plus6: int, num6: int, chnl: int, x1: float, x2: float, y1: float, y2: float) -> Advance:
		return cls(plus4=plus4, num4=num4, plus6=plus6, num6=num6, chnl=chnl, x1_1=x1, x1_2=x1, x2_1=x2, x2_2=x2, y1_1=y1, y1_2=y1, y2_1=y2, y2_2=y2)
	
	@classmethod
	def read(cls, stream: Stream) -> Advance:
		return cls(*cls.__struct__.unpack(stream[44]))
	
	def pack(self) -> bytes:
		return self.__struct__.pack(self.plus4, self.num4, self.plus6, self.num6, self.chnl, self.x1_1, self.y1_1, self.x2_1, self.y1_2, self.x2_2, self.y2_1, self.x1_2, self.y2_2)



	

@dataclass
class Character:
	bearingX1_1: float
	bearingX1_2: float
	bearingY1_1: float
	bearingY1_2: float
	bearingX2_1: float
	bearingX2_2: float
	bearingY2_1: float
	bearingY2_2: float
	x_lo_1: float
	x_hi_1: float
	x_lo_2: float
	x_hi_2: float
	y_lo_1: float
	y_hi_1: float
	y_lo_2: float
	y_hi_2: float
	
	@classmethod
	def read(cls, stream: Stream) -> Character:
		return cls(*unpack("16f", stream[64]))
	
	@classmethod
	def from_single(cls, x1: float, x2: float, y1: float, y2: float, x_lo: float, x_hi: float, y_lo: float, y_hi: float) -> Character:
		return cls(
			bearingX1_1=x1, bearingX1_2=x1, bearingX2_1=x2, bearingX2_2=x2, bearingY1_1=y1, bearingY1_2=y1, bearingY2_1=y2, bearingY2_2=y2,
			x_lo_1=x_lo, x_lo_2=x_lo, x_hi_1=x_hi, x_hi_2=x_hi, y_lo_1=y_lo, y_lo_2=y_lo, y_hi_1=y_hi, y_hi_2=y_hi,
		)
	
	def point_x(self, width: int):
		return self.x_lo_1 * width
	
	def point_y(self, height: int):
		return self.y_lo_1 * height
	
	def point_w(self, width: int):
		return (self.x_hi_1 * width) - (self.x_lo_1 * width)
	
	def point_h(self, height: int):
		return (self.y_hi_1 * height) - (self.y_lo_1 * height)

	def toEntry(self, width: int, height: int, lineHeight: float, size: float) -> CharacterEntry:
		return CharacterEntry(
			idx=None,
			x=int(round(self.point_x(width), 2)),
			y=int(round(self.point_y(height), 2)),
			w=int(round(self.point_w(width), 2)),
			h=int(round(self.point_h(height), 2)),
			x_o=self.bearingX1_1 * size,
			y_o=lineHeight - self.bearingY2_1 * size - self.point_h(height),
			x_adv=None,
			page=0,
			chnl=None,
		)
	
	def pack(self) -> bytes:
		return pack("16f", self.bearingX1_1, self.bearingY2_1, self.x_lo_1, self.y_hi_1, self.bearingX2_1, self.bearingY2_2, self.x_hi_1, self.y_hi_2, self.bearingX2_2, self.bearingY1_1,
		            self.x_hi_2, self.y_lo_1, self.bearingX1_2, self.bearingY1_2, self.x_lo_2, self.y_lo_2)


@dataclass
class CharacterEntry:
	idx: None
	x: int
	y: int
	w: int
	h: int
	x_o: float
	y_o: float
	x_adv: float | None
	page: int
	chnl: int | None



@dataclass
class Point:
	x: float
	y: float
	w: float
	h: float
	
	def uv_n(self, height: int):
		return self.y / height
	
	def uv_s(self, height: int):
		return (self.y + self.h) / height
	
	def uv_e(self, width: int):
		return (self.x + self.w) / width
	
	def uv_w(self, width: int):
		return self.x / width


@dataclass
class Unknown:
	n1: int
	n2: int
	n3: int
	n4: int
	n5: int
	n6: int
	
	@classmethod
	def read(cls, stream: Stream) -> Unknown:
		return cls(*unpack("6H", stream[12]))
	
	def pack(self) -> bytes:
		return pack("6H", self.n1, self.n2, self.n3, self.n4, self.n5, self.n6)



@dataclass
class BinaryFont:
	version: FontVersionEnum
	
	textureWidth: int
	textureHeight: int
	textureBytes: bytes
	
	characters: list[Character]     = field(default_factory=list)
	unknown:    list[Unknown]       = field(default_factory=list)
	advance:    list[Advance]       = field(default_factory=list)
	ids:        list[int]           = field(default_factory=list)
	kerning:    list[Kernel]        = field(default_factory=list)
	fontSize:   float               = field(default=0.0)
	lineHeight: float               = field(default=0.0)
	
	def __init__(self, stream: Stream):
		self.version = FontVersionEnum(int(stream))
		
		self.char_count = int(stream) // 4
		self.characters = [x for x in (CharDesc * self.char_count).from_buffer_copy(stream[64 * self.char_count])]
		
		self.unknown_entries = int(stream) // 6
		self.unknown = [x for x in (UnknDesc * self.char_count).from_buffer_copy(stream[24 * self.char_count])]
		
		self.advance_count = int(stream)
		self.advance = [x for x in (AdvcDesc * self.char_count).from_buffer_copy(stream[24 * self.char_count])]
		
		idvals = list()
		for i in range(0xFFFF + 1):
			idx = stream.i2
			if idx != 0:
				self.ids.append(i)
				idvals.append(idx)
		self.ids.insert(0, self.ids[0] - 1)
		
		self.kerns_count = int(stream)
		for _ in range(self.kerns_count):
			if self.version == FontVersionEnum.QBR:
				self.kerning.append(Kernel.read_8(stream))
			elif self.version == FontVersionEnum.AWR:
				self.kerning.append(Kernel.read_12(stream))
			else:
				raise ValueError("Unsupported font version")
		
		if self.version in [FontVersionEnum.AW1, FontVersionEnum.AWR]:
			self.textureSize = int(stream)
			self.textureUnknownVal = b'\x00\x00\x00\x00\x00\x00\x00\x00'
		elif self.version == FontVersionEnum.QBR:
			self.textureSize = 0
			self.textureUnknownVal = stream[8]
		
		texturePos = stream.tell()
		stream.seek(12, 1)
		
		self.textureHeight = int(stream)
		self.textureWidth = int(stream)
		
		stream.seek(texturePos)
		self.textureBytes = stream.read()
		
		sizes = []
		lineHeights = []
		
		for idx, char in enumerate(self.characters):
			size = (char.point_h(self.textureHeight) / (char.bearingY1_1 - char.bearingY2_1)) if char.bearingY1_1 != char.bearingY2_1 else 0.0
			sizes.append(size)
			lineHeights.append(-self.advance[idx].y2_1 * size + char.point_h(self.textureHeight) + char.bearingY2_1 * size)
		self.fontSize = max(set(sizes), key=sizes.count)
		self.lineHeight = max(set(lineHeights), key=lineHeights.count)
	
	def write(self, writer: BinaryIO):
		writer.write(self.version.value.to_bytes(4, "little", signed=False))
		
		# char block
		writer.write((len(self.characters) * 4).to_bytes(4, "little", signed=False))
		writer.write(b''.join(c.pack() for c in self.characters))
		
		# unknown block
		writer.write((len(self.unknown) * 6).to_bytes(4, "little", signed=False))
		last_entry = None
		for i in range(len(self.characters)):
			# If we reached the end of the unknown list, write the last unknown entry till the end
			if last_entry == self.unknown[-1]:
				writer.write(self.unknown[-1].pack())
			else:
				writer.write(self.unknown[i].pack())
				last_entry = self.unknown[i]
		
		# advance block
		writer.write(len(self.advance).to_bytes(4, "little", signed=False))
		writer.write(b''.join(a.pack() for a in self.advance))
		
		# id block
		id_table = {i: 0 for i in range(0xFFFF + 1)}
		base_id = 0
		for idx in self.ids:
			id_table[idx] = base_id
			base_id += 1
		for idx in id_table.values():
			writer.write(idx.to_bytes(2, "little", signed=False))
		
		# kerning block
		writer.write(len(self.kerning).to_bytes(4, "little", signed=False))
		writer.write(b''.join(kerning.pack() for kerning in self.kerning))
		
		# texture block
		if self.version in [FontVersionEnum.AW1, FontVersionEnum.AWR]:
			writer.write(len(self.textureBytes).to_bytes(4, "little", signed=False))
		elif self.version == FontVersionEnum.QBR:
			writer.write(self.textureUnknownVal)
		writer.write(self.textureBytes)
	
	def convert_to_bmfont(self) -> tuple[list[CharacterEntry], list[Kernel]]:
		characters = [char.toEntry(self.textureWidth, self.textureHeight, self.lineHeight, self.fontSize) for char in self.characters]
		for idx, id_value in enumerate(self.ids):
			characters[idx].idx = id_value
		
		for idx, advance in enumerate(self.advance):
			characters[idx].x_adv = advance.x2_1 * self.fontSize
			if advance.chnl == 0:
				characters[idx].chnl = 4
			elif advance.chnl == 1:
				characters[idx].chnl = 2
			elif advance.chnl == 2:
				characters[idx].chnl = 1
		
		kernings = []
		if self.version == FontVersionEnum.QBR:
			for kerning in self.kerning:
				kerning.val = kerning.val * self.fontSize
				kernings.append(kerning)
		elif self.version == FontVersionEnum.AWR:
			for kerning in self.kerning:
				kerning.val = kerning.val / self.fontSize
				kernings.append(kerning)
		
		return characters, kernings
	
	def apply_bmfont_to_binfnt(self, bmfont: list[str]):
		info_line = bmfont[0].split(" ")
		info = {x.split("=")[0]: x.split("=")[1].strip() for x in info_line[1:]}
		self.fontSize = float(info["size"])
		
		common_line = bmfont[1].split(" ")
		common = {x.split("=")[0]: x.split("=")[1].strip() for x in common_line[1:]}
		self.lineHeight = float(common["lineHeight"])
		self.textureWidth = int(common["scaleW"])
		self.textureHeight = int(common["scaleH"])
		
		page = {x.split("=")[0]: x.split("=")[1].strip() for x in bmfont[2].split(" ")[1:]}
		chars = {x.split("=")[0]: x.split("=")[1].strip() for x in bmfont[3].split(" ")[1:]}
		expected_chars = int(chars["count"])
		
		self.characters.clear()
		
		num4 = self.advance[0].num4
		num6 = self.advance[0].num6
		
		self.advance.clear()
		self.ids.clear()
		
		for i in range(expected_chars):
			char: dict[str, str | int] = {x.split("=")[0]: x.split("=")[1].strip() for x in bmfont[4 + i].split(" ")[1:]}
			
			if int(char["width"]) == 0 and int(char["height"]) == 0:
				char["width"] = 6
				char["height"] = 6
			
			point = Point(x=float(char["x"]), y=float(char["y"]), w=int(char["width"]), h=int(char["height"]))
			binfntChar = Character.from_single(
				x1=float(char["xoffset"]) / self.fontSize,
				x2=(float(char["xoffset"]) + float(char["width"])) / self.fontSize,
				y1=(self.lineHeight - float(char["yoffset"])) / self.fontSize,
				y2=(self.lineHeight - float(char["yoffset"]) - int(char["height"])) / self.fontSize,
				x_lo=point.uv_w(self.textureWidth), y_lo=point.uv_n(self.textureHeight),
				x_hi=point.uv_e(self.textureWidth), y_hi=point.uv_s(self.textureHeight),
			)
			
			if int(char["id"]) in [9, 10, 13, 32]:
				binfntChar.bearingX1_1 = 0
				binfntChar.bearingY2_1 = 0
				binfntChar.bearingX2_1 = 0
				binfntChar.bearingY1_1 = 0
			
			self.characters.append(binfntChar)
			
			match int(char["chnl"]):
				case 2:
					chnl = 1
				case 1:
					chnl = 2
				case _:
					chnl = 0
			
			advance = Advance.from_single(
				plus4=num4 * i, num4=num4, plus6=num6 * i, num6=num6,
				chnl=chnl, x1=0, x2=float(char["xadvance"]) / self.fontSize,
				y1=(-float(char["yoffset"]) / self.fontSize) - int(char["height"]) / self.fontSize, y2=-float(char["yoffset"]) / self.fontSize,
			)
			
			self.advance.append(advance)
			self.ids.append(int(char["id"]))
		
		kernings_line = bmfont[4 + expected_chars].split(" ")
		kernings = {x.split("=")[0]: x.split("=")[1].strip() for x in kernings_line[1:]}
		expected_kernings = int(kernings["count"])
		
		self.kerning.clear()
		
		for i in range(expected_kernings):
			kerning_line = bmfont[5 + expected_chars + i].split(" ")
			kerning = {x.split("=")[0]: x.split("=")[1].strip() for x in kerning_line[1:]}
			
			if self.version in [FontVersionEnum.AW1, FontVersionEnum.AWR]:
				amount = float(kerning["amount"]) * self.fontSize
			elif self.version == FontVersionEnum.QBR:
				amount = float(kerning["amount"]) / self.fontSize
			else:
				amount = None
			
			self.kerning.append(Kernel(a=int(kerning["first"]), b=int(kerning["second"]), val=amount))
		
		return page["file"].strip('"')
	
	def decompile(self, name: str, output_dir: Path, separate_chars: bool = False):
		characters, kernings = self.convert_to_bmfont()
		fnt_suffix = ".fnt"
		bitmap_suffix = ".png" if self.version.value == 7 else ".dds"
		
		output_dir.mkdir(parents=True, exist_ok=True)
		fnt_file = output_dir / (name + fnt_suffix)
		bitmap_file = output_dir / (name + bitmap_suffix)
		
		with open(fnt_file, "w") as f:
			f.write(f'info face="" size={self.fontSize} bold=0 italic=0\n')
			f.write(f"common lineHeight={self.lineHeight} base=0 scaleW={self.textureWidth} scaleH={self.textureHeight} pages=1\n")
			f.write(f'page id=0 file="{bitmap_file.name}"\n')
			f.write(f"chars count={len(characters)}\n")
			for char in characters:
				f.write(
					f"char id={char.idx} x={char.x} y={char.y} width={round(char.w)} height={round(char.h)} xoffset={char.x_o} yoffset={char.y_o} xadvance={char.x_adv} page={char.page} chnl={char.chnl}\n")
			f.write(f"kernings count={len(kernings)}\n")
			for kerning in kernings:
				f.write(f"kerning first={kerning.a} second={kerning.b} amount={kerning.val}\n")
		
		if self.version.value == 7:
			bitmap = Image.open(BytesIO(convert_r16f_to_bgra8(Stream(self.textureBytes))))
			
			if separate_chars:
				char_bitmap_dir = output_dir / "chars"
				char_bitmap_dir.mkdir(parents=True, exist_ok=True)
				
				for char in characters:
					if char.w == 0 or char.h == 0:
						continue
					char_bitmap = bitmap.crop((char.x, char.y, char.x + char.w, char.y + char.h))
					char_bitmap.save(char_bitmap_dir / f"{char.idx}.png")
			else:
				with open(bitmap_file, "wb") as f:
					bitmap.save(f, "PNG")
		else:
			with open(bitmap_file, "wb") as f:
				f.write(self.textureBytes)
	
	def compile(self, modified_file: Path, output_file: Path | None = None) -> None:
		if modified_file.suffix != ".fnt":
			raise ValueError(f"{modified_file} is not a .fnt file!")

		with open(modified_file, "r") as f:
			bitmap_file_path = self.apply_bmfont_to_binfnt(f.readlines())
		
		if self.version in [3, 4] and not bitmap_file_path.endswith(".dds"):
			raise ValueError(f"{bitmap_file_path} is not a .dds file! Alan Wake fonts require a .dds texture.")
		
		if self.version.value == 7 and not bitmap_file_path.endswith(".png"):
			raise ValueError(f"{bitmap_file_path} is not a .png file! Quantum Break fonts require a .png bitmap.")
		
		bitmap_file_path = modified_file.parent / bitmap_file_path
		
		if not bitmap_file_path.exists():
			if self.version in [3, 4]:
				raise AssertionError(f"{bitmap_file_path} does not exist!")
			
			elif self.version.value == 7:
				# Check if the char directory exists, and if it does, compile the characters into a single bitmap
				char_dir = modified_file.parent / "chars"
				
				if not char_dir.exists():
					raise AssertionError(
						f"Neither {char_dir} or {bitmap_file_path} exist! Please ensure that the character bitmaps are in a directory named 'chars' in the same directory as the .fnt file.")
				
				compiled_bitmap = Image.new("RGBA", (self.textureWidth, self.textureHeight), (255, 255, 255, 127))
				for i, char in enumerate(self.characters):
					idx = self.ids[i]
					if not (char_dir / f"{idx}.png").exists():
						continue
					point = char.toEntry(self.textureWidth, self.textureHeight, self.lineHeight, self.fontSize)
					bitmap_char = Image.open(char_dir / f"{idx}.png")
					compiled_bitmap.paste(bitmap_char, (point.x, point.y))
			else:
				raise AssertionError(f"{bitmap_file_path} unsupported binfnt version: {self.version}")
		else:
			compiled_bitmap = Image.open(bitmap_file_path)
		
		rgba_texture = BytesIO()
		compiled_bitmap.save(rgba_texture, "DDS")
		rgba_texture = rgba_texture.getvalue()
		
		if self.version.value == 7:
			self.textureBytes = convert_bgra8_to_r16f(Stream(rgba_texture))
		else:
			self.textureBytes = rgba_texture
		
		if output_file:
			output_file = Path(output_file)
		else:
			output_file = modified_file.with_suffix(".binfnt")
		
		with open(output_file, "wb") as f:
			self.write(f)

def convert_r16f_to_bgra8(r16f: Stream) -> bytes:
	r16f.seek(12)
	
	textureHeight = int(r16f)
	textureWidth = int(r16f)
	
	r16f.seek(84)
	
	fourcc = int(r16f)
	if fourcc != 111:
		raise ValueError(f"Texture is not in R16_FLOAT pixel format! (Texture pixel format is: {fourcc})")
	
	r16f.seek(128)
	
	# Write new header
	bgra8 = bytearray()
	bgra8 += b"DDS |\x00\x00\x00\x0f\x10\x02\x00" + textureHeight.to_bytes(4, "little") + textureWidth.to_bytes(4, "little") + (textureWidth * 2).to_bytes(4, "little")
	bgra8 += b"\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00A\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\x00\x00\x00\x00\xff\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	
	# Convert R16F to BGRA8
	for _ in range(textureWidth * textureHeight):
		hGray = r16f.f2
		# normalize alpha to [-9,9]
		normalized_value = ((9 - hGray) * 255) / 18
		if normalized_value < 0:
			alpha = 0
		elif normalized_value > 255:
			alpha = 255
		else:
			alpha = int(normalized_value)
		
		if alpha > 0:
			bgra8 += pack("BBBB", 255, 255, 255, alpha)
		else:
			bgra8 += pack("BBBB", 0, 0, 0, 0)
	return bytes(bgra8)


def convert_bgra8_to_r16f(bgra8: Stream) -> bytes:
	bgra8.seek(12)
	
	textureHeight = int(bgra8)
	textureWidth = int(bgra8)
	
	bgra8.seek(128)
	
	r16f = bytearray
	r16f += b"DDS |\x00\x00\x00\x0f\x10\x02\x00"
	r16f += textureHeight.to_bytes(4, "little")
	r16f += textureWidth.to_bytes(4, "little")
	r16f += (textureWidth * 2).to_bytes(4, "little")
	r16f += b"\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00o\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	
	# Read BGRA8 and convert to grayscale R16F
	for _ in range(textureWidth * textureHeight):
		b, g, r, a = bgra8.read(4)
		
		# Normalize alpha to [-9,9]
		hGray = -(18 * a / 255.0 - 9.0)
		
		if a > 0:
			# Convert hGray to float16
			r16f += pack("f", hGray)
		else:
			r16f += pack("h", 32767)
	
	return bytes(r16f)



