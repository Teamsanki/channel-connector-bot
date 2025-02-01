import { useState, useEffect } from "react";
import { collection, getDocs, addDoc, serverTimestamp } from "firebase/firestore";
import { db, auth } from "@/lib/firebase";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import Navigation from "@/components/Navigation";
import { useToast } from "@/components/ui/use-toast";
import { Camera, Send } from "lucide-react";

const Index = () => {
  const [posts, setPosts] = useState<any[]>([]);
  const [newPost, setNewPost] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const querySnapshot = await getDocs(collection(db, "posts"));
      const postsData = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setPosts(postsData);
    } catch (error) {
      console.error("Error fetching posts:", error);
      toast({
        title: "Error",
        description: "Failed to load posts",
        variant: "destructive"
      });
    }
  };

  const handlePost = async () => {
    if (!newPost.trim() || !auth.currentUser) return;

    try {
      await addDoc(collection(db, "posts"), {
        content: newPost,
        userId: auth.currentUser.uid,
        username: auth.currentUser.displayName,
        timestamp: serverTimestamp()
      });
      setNewPost("");
      fetchPosts();
      toast({
        title: "Success",
        description: "Post created successfully"
      });
    } catch (error) {
      console.error("Error creating post:", error);
      toast({
        title: "Error",
        description: "Failed to create post",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="pb-20">
      <div className="fixed top-0 left-0 right-0 bg-white border-b p-4 z-10">
        <div className="flex gap-2">
          <Input
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="What's on your mind?"
            className="flex-1"
          />
          <Button onClick={handlePost}>
            <Send className="h-4 w-4 mr-2" />
            Post
          </Button>
          <Button variant="outline">
            <Camera className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="mt-20 p-4 space-y-4">
        {posts.map((post) => (
          <Card key={post.id}>
            <CardHeader className="font-bold">{post.username}</CardHeader>
            <CardContent>{post.content}</CardContent>
          </Card>
        ))}
      </div>

      <Navigation />
    </div>
  );
};

export default Index;