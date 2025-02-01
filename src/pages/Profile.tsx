import { useEffect, useState } from "react";
import { auth, db } from "@/lib/firebase";
import { collection, getDocs, query, where } from "firebase/firestore";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Navigation from "@/components/Navigation";
import { LogOut } from "lucide-react";

const Profile = () => {
  const [userPosts, setUserPosts] = useState<any[]>([]);

  useEffect(() => {
    const fetchUserPosts = async () => {
      if (!auth.currentUser) return;
      
      const q = query(
        collection(db, "posts"),
        where("userId", "==", auth.currentUser.uid)
      );
      
      const querySnapshot = await getDocs(q);
      const postsData = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setUserPosts(postsData);
    };
    
    fetchUserPosts();
  }, []);

  const handleLogout = () => {
    auth.signOut();
  };

  return (
    <div className="pb-20">
      <div className="p-4">
        <Card className="mb-4">
          <CardHeader className="flex flex-row justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">
                {auth.currentUser?.displayName}
              </h2>
              <p className="text-gray-500">{auth.currentUser?.email}</p>
            </div>
            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </CardHeader>
        </Card>

        <h3 className="text-xl font-bold mb-4">Your Posts</h3>
        <div className="space-y-4">
          {userPosts.map((post) => (
            <Card key={post.id}>
              <CardContent className="pt-4">
                {post.content}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      <Navigation />
    </div>
  );
};

export default Profile;