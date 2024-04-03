export default function Home() {
  const uploadFile = async (formData: FormData) => {
    "use server";

    const response = await fetch("http://127.0.0.1:8000/extract", {
      method: "POST",
      headers: {
        "Content-Type": "multipart/formdata",
        "Content-Disposition": 'form-data; name="pdf"'
      },
      body: formData
    });
    console.log(await response.json());
  }

  return (
    <main>
      <form action={uploadFile}>
        <input name="pdf" type="file" accept="application/pdf" />
        <button type="submit">Upload</button>
      </form>
    </main>
  );
}
