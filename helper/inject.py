import lief

MARKER1 = b"FUSED__START__1"
MARKER2 = b"FUSED__START__2"
MARKER3 = b"FUSED__END_____"

def inject(app1, app2):
    with open(app1, "rb") as f:
        app1_bytes = f.read()

    with open(app2, "rb") as f:
        app2_bytes =f.read()

    payload = (
        MARKER1 + app1_bytes +
        MARKER2 + app2_bytes +
        MARKER3
    )

    pe1 = lief.parse(app1)
    if pe1.optional_header.magic == lief.PE.PE_TYPE.PE32:
        stub_path = "stub.exe"
    else:
        stub_path = "stub64.exe"

    pe = lief.parse(stub_path)
    section = lief.PE.Section(".fused")
    section.content = list(payload)
    section.characteristics = (
        lief.PE.Section.CHARACTERISTICS.MEM_READ |
        lief.PE.Section.CHARACTERISTICS.CNT_INITIALIZED_DATA
    )
    pe.add_section(section)

    return pe