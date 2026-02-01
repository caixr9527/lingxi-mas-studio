interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function Page({ params }: PageProps) {
  const { id } = await params;
  return <div className="bg-red-100">会话列表: {id}</div>;
}
