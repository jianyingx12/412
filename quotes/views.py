from django.shortcuts import render
import random

# Create your views here.
QUOTES = [
    "I'm old. I got arthritis, I got rheumatism, I got bursitis, but I don't need no sense of humor.",
    "You need to stop all that crying before I come in there and give you something to cry about!",
    "Peace be still? That ain't what the Bible says! It says 'Get up and fight!'",
    "I ain't scared of no popo! Call the popo!",
    "Honey you in jail cause of what you did, learn to take responsibility for yourself… I can't stand folks wanna be the victim…yo mama and yo daddy gave you life…it's up to you to make something out of it.",
    "A lie don't care who tells it, just as long as it gets told.",
    "I'm not bitter, I'm better!",
    "I'm tryin to have a conversation with you and all you doin' is breathin'!",
    "You are grown. You is old. You got hair on your face, you is old!",
]

IMAGES = [
    "https://s.abcnews.com/images/Entertainment/tyler-perry-madea-ht-jpo-171026.jpg",
    "https://www.usatoday.com/gcdn/presto/2018/10/31/USAT/1abf90c9-70f5-4734-8950-1d978c60a015-XXX_IMG_BOO_2_EXCLUSIVE_1_1_K1K24G8R.JPG",
    "https://raycornelius.com/wp-content/uploads/2016/01/tyler-perry-as-madea-in-madea-s-witness-protection.jpg",
    "https://variety.com/wp-content/uploads/2013/06/boo-a-madea-halloween.jpg",
    "https://dbknews.s3.amazonaws.com/uploads/2022/02/Screenshot_20220227-180943_YouTube.jpg",
    "https://sciencefiction.com/wp-content/uploads/2017/10/Boo-A-Madea-Halloween-Tyler-Perry-Waze-Navigation.jpg",
    "https://pyxis.nymag.com/v1/imgs/a39/4c3/07e7f481c52ae02b9de38fbf2f2235186c-8-Tyler-Perry-Madea.1x.rsocial.w1200.jpg",
    "https://static1.colliderimages.com/wordpress/wp-content/uploads/2022/04/madeas-family-reunion-movie-bg-landscape-01.jpg",

]

# display one random quote and image
def quotes(request):
    random_quote = random.choice(QUOTES)
    random_image = random.choice(IMAGES)
    context = {
        'quote': random_quote,
        'image': random_image,
    }
    return render(request, 'quotes/quote.html', context)

# display all images and quotes
def show_all(request):
    context = {
        'quotes': QUOTES,
        'images': IMAGES,
    }
    return render(request, 'quotes/show_all.html', context)

# display info about the person
def about(request):
    bio_info = "Mabel “Madea” Simmons is a fictional character created by Tyler Perry, known for her tough love and sharp wit. She first appeared in 1999 in a play called I Can Do Bad All by Myself and has since starred in numerous films. Madea is beloved for her hilarious take on life's challenges."
    creator_info = "Created by Jianying Liu, a CS student who likes comedy shows."
    context = {
        'bio': bio_info,
        'creator': creator_info,
    }
    return render(request, 'quotes/about.html', context)