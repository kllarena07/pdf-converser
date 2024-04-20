export default function Home() {
  const uploadFile = async (formData: FormData) => {
    "use server";

    const response = await fetch("http://127.0.0.1:8000/extract/", {
      method: "POST",
      body: formData
    });
    console.log(await response.json());
  }

  const queryFile = async (formData: FormData) => {
    "use server";

    const response = await fetch("http://127.0.0.1:8000/query/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: formData.get("query"),
        filename: "lab7"
      })
    });
    console.log(await response.json());
  }

  return (
    <main>
      <form action={uploadFile}>
        <label>
          <input name="pdf" type="file" accept="application/pdf" />
        </label>
        <button type="submit">Upload</button>
      </form>
      <form action={queryFile}>
        <label>
          <input name="query" type="text" placeholder="Message uploaded PDF" />
        </label>
        <button type="submit">Search</button>
      </form>
    </main>
  );
}
